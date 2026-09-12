"""
The real running loop: warm-up -> calibrate -> read -> classify -> alert -> log -> sync.

    warm-up (clean-air samples)
      -> Calibrator.set_baseline()
      -> loop:
           read sensors -> Calibrator.to_ratio() -> accumulate a trace window
           -> extract_features() -> Classifier.predict() -> AlertEngine.evaluate()
           -> AlertOutputs.fire() + EventLog.record()
           -> try MqttPublisher.publish(); on failure, leave it queued in EventLog
      -> a separate sync pass drains EventLog.pending() whenever connectivity returns

Run for real (on a Pi, with a broker configured):
    python -m handheld.main --broker-host 192.168.1.50

Run anywhere, no hardware, no broker -- generates plausible fake readings instead:
    python -m handheld.main --simulate

--- Merge note --------------------------------------------------------------------------
features.py, model.py and eventlog.py were built by a parallel agent and have since landed
(2026-09-12) -- this module is now wired against their REAL shapes:

    features.py:  extract_features(trace: list[dict[str, float]]) -> dict[str, float]
    model.py:     load_model(path: str) -> RandomForestModel   (joblib.load, raises
                  FileNotFoundError if missing -- caller falls back to a heuristic stub)
    eventlog.py:  class EventLog:
                      def __init__(self, db_path: str | Path): ...
                      def record(self, event: dict) -> EventRecord: ...   # .id, .payload
                      def mark_synced(self, record_id: int) -> None: ...
                      def pending(self) -> list[EventRecord]: ...

The local fallbacks below (`_DummyModel`, `_FallbackEventLog`, marked `# ponytail:`) only
activate if one of those three modules is ever removed/broken -- they mirror the real
interface exactly so no other code here needs to change either way.
-------------------------------------------------------------------------------------------
"""
import argparse
import random
import time
from datetime import datetime, timezone
from statistics import mean

from handheld.calibration import Calibrator
from handheld.classifier import Classifier, ClassificationResult
from handheld.alerts import AlertEngine, ZoneConfig

try:
    from handheld.features import extract_features
except ImportError:
    def extract_features(trace: list[dict[str, float]]) -> dict[str, float]:
        # ponytail: mean-per-channel stand-in for the real feature engineering (variance,
        # slope, cross-sensor ratios, ...). Upgrade: delete once handheld.features exists.
        channels = trace[0].keys()
        return {f"{ch}_mean": mean(sample[ch] for sample in trace) for ch in channels}

try:
    from handheld.model import load_model
except ImportError:
    load_model = None


class _DummyModel:
    """ponytail: naive heuristic stand-in for a trained model.joblib -- classifies purely on
    average deviation of the (ratio-based) features from 1.0 (baseline). No real accuracy,
    just enough to exercise clean/review/alert end to end. Upgrade: delete once model.py +
    a trained model.joblib exist.
    """

    def predict_proba(self, features: dict[str, float]) -> dict[str, float]:
        values = [v for v in features.values() if isinstance(v, (int, float))]
        deviation = mean(abs(v - 1.0) for v in values) if values else 0.0
        if deviation < 0.15:
            return {"clean": 0.9, "unknown": 0.1}
        if deviation < 0.4:
            return {"clean": 0.3, "unknown": 0.7}
        return {"narcotic_suspect": 0.85, "clean": 0.15}


class _FallbackRecord:
    """ponytail: minimal stand-in for eventlog.EventRecord -- just the two fields call sites
    below actually use (.id, .payload)."""

    def __init__(self, id_: int, payload: dict):
        self.id = id_
        self.payload = payload


class _FallbackEventLog:
    """ponytail: in-memory stand-in for eventlog.py's persistent hash-chained log -- nothing
    survives a restart, no hash chain. Mirrors EventLog's real method names/return shapes
    exactly so run_scan()/drain_pending() don't need an ImportError branch of their own.
    Upgrade: delete once handheld.eventlog is confirmed always present (it already exists
    as of 2026-09-12 -- this only guards against it being removed/broken later)."""

    def __init__(self, db_path=None):
        del db_path  # in-memory only; accepted for constructor-shape parity with the real EventLog
        self._events: dict[int, dict] = {}
        self._next_id = 1

    def record(self, event: dict) -> _FallbackRecord:
        record = _FallbackRecord(self._next_id, event)
        self._events[record.id] = event
        self._next_id += 1
        return record

    def mark_synced(self, record_id: int) -> None:
        self._events.pop(record_id, None)

    def pending(self) -> list[_FallbackRecord]:
        return [_FallbackRecord(rid, payload) for rid, payload in self._events.items()]


try:
    from handheld.eventlog import EventLog
except ImportError:
    EventLog = _FallbackEventLog


# --- sensor access -------------------------------------------------------------------

SENSOR_CHANNELS = ("mq135", "mq3", "mq2", "gas_resistance", "temperature", "humidity", "pressure")

_SIM_BASELINE = {
    "mq135": 2.0, "mq3": 1.0, "mq2": 1.0,
    "gas_resistance": 50_000.0, "temperature": 28.0, "humidity": 45.0, "pressure": 1005.0,
}
# Multiplier applied to the MQ + gas-resistance channels for each simulated scan profile --
# environmental channels (temp/humidity/pressure) get much smaller jitter, real air doesn't
# swing much scan to scan.
_SIM_PROFILES = {
    "clean": 1.0,
    "review": 1.25,
    "alert": 1.8,
}


def read_simulated(profile: str, rng: random.Random) -> dict[str, float]:
    multiplier = _SIM_PROFILES[profile]
    reading = {}
    for channel, base in _SIM_BASELINE.items():
        if channel in ("temperature", "humidity", "pressure"):
            reading[channel] = base * rng.uniform(0.99, 1.01)
        else:
            reading[channel] = base * multiplier * rng.uniform(0.95, 1.05)
    return reading


def read_hardware(adc, bme) -> dict[str, float]:
    reading = adc.read()
    reading.update(bme.read())
    return reading


# --- pipeline --------------------------------------------------------------------------

def collect_baseline(read_fn, samples: int) -> dict[str, float]:
    clean_air_samples = [read_fn() for _ in range(samples)]
    return Calibrator().set_baseline(clean_air_samples)


def run_scan(*, read_fn, calibrator, baseline, window_size, classifier, zone,
             outputs, eventlog: "EventLog", publisher, device_id: str) -> dict:
    trace = []
    for _ in range(window_size):
        raw = read_fn()
        trace.append(calibrator.to_ratio(raw, baseline))

    features = extract_features(trace)
    classification = classifier.predict(features)
    decision = AlertEngine().evaluate(classification, zone)
    fired = outputs.fire(decision.tier)

    event = {
        "device_id": device_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "label": classification.label,
        "confidence": classification.confidence,
        "is_unknown": classification.is_unknown,
        "tier": decision.tier,
        "escalate": decision.escalate,
        "outputs_fired": list(fired),
    }
    record = eventlog.record(event)

    published = False
    try:
        published = publisher.publish(event)
    except Exception as exc:
        print(f"  [sync] publish raised {exc!r}, leaving event {record.id} queued")
    if published:
        eventlog.mark_synced(record.id)

    print(f"  [scan] label={classification.label!r} confidence={classification.confidence:.2f} "
          f"tier={decision.tier} outputs={fired} published={published}")
    return event


def drain_pending(eventlog: "EventLog", publisher) -> int:
    """Sync pass: try to publish everything still queued. Returns how many got through."""
    sent = 0
    for record in eventlog.pending():
        try:
            ok = publisher.publish(record.payload)
        except Exception:
            ok = False
        if ok:
            eventlog.mark_synced(record.id)
            sent += 1
    return sent


# --- simulate-mode stand-ins for hardware/network (never import spidev/gpiozero/paho) ---

class _SimulatedOutputs:
    def fire(self, tier: str) -> tuple[str, ...]:
        from handheld.outputs import AlertOutputs
        outputs = AlertOutputs.TIER_OUTPUTS.get(tier, ())
        print(f"  [gpio-sim] would fire: {outputs}")
        return outputs


class _SimulatedPublisher:
    """Randomly fails to simulate Wi-Fi dropouts, so --simulate demos the offline queue too."""

    def __init__(self, rng: random.Random, failure_rate: float = 0.35):
        self._rng = rng
        self._failure_rate = failure_rate

    def publish(self, event: dict) -> bool:
        ok = self._rng.random() > self._failure_rate
        print(f"  [mqtt-sim] publish attempt -> {'OK' if ok else 'FAILED (no connectivity)'}")
        return ok


def main():
    parser = argparse.ArgumentParser(description="SenseGuard handheld detection loop")
    parser.add_argument("--simulate", action="store_true",
                         help="Generate fake sensor readings and skip real GPIO/MQTT -- runs anywhere.")
    parser.add_argument("--cycles", type=int, default=6, help="Number of scan cycles to run.")
    parser.add_argument("--window-size", type=int, default=5, help="Raw samples per scan.")
    parser.add_argument("--baseline-samples", type=int, default=5, help="Clean-air samples for warm-up.")
    parser.add_argument("--alert-threshold", type=float, default=0.75)
    parser.add_argument("--device-id", default="handheld-01")
    parser.add_argument("--broker-host", default="localhost")
    parser.add_argument("--broker-port", type=int, default=1883)
    parser.add_argument("--topic", default="senseguard/events")
    parser.add_argument("--model-path", default="handheld/model.joblib")
    parser.add_argument("--db-path", default="handheld_events.db",
                         help="SQLite path for the hash-chained event log.")
    parser.add_argument("--seed", type=int, default=None, help="Simulate-mode RNG seed.")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    zone = ZoneConfig(alert_threshold=args.alert_threshold)

    _current_profile = ["clean"]

    if args.simulate:
        print("=== SIMULATE MODE: no real sensors, GPIO, or MQTT broker will be touched ===")
        def read_fn():
            # One profile per scan (not per raw sample) -- a real sniff is one consistent
            # air sample over the window, not a random mix each reading.
            return read_simulated(_current_profile[0], rng)
        outputs = _SimulatedOutputs()
        publisher = _SimulatedPublisher(rng)
    else:
        from handheld.sensors import AdcReader, Bme688Reader
        from handheld.outputs import AlertOutputs
        from handheld.sync import MqttPublisher
        adc, bme = AdcReader(), Bme688Reader()
        read_fn = lambda: read_hardware(adc, bme)  # noqa: E731
        outputs = AlertOutputs()
        publisher = MqttPublisher(args.broker_host, args.broker_port, args.topic)

    if load_model is not None:
        try:
            model = load_model(args.model_path)
            print(f"Loaded trained model from {args.model_path}")
        except FileNotFoundError:
            print(f"No trained model at {args.model_path} yet -- falling back to heuristic stub.")
            model = _DummyModel()
    else:
        print("handheld.model not built yet -- falling back to heuristic stub.")
        model = _DummyModel()

    classifier = Classifier(model=model, reject_threshold=args.alert_threshold)
    calibrator = Calibrator()
    eventlog = EventLog(args.db_path)

    print(f"Warming up: collecting {args.baseline_samples} clean-air samples for baseline...")
    baseline_read_fn = (lambda: read_simulated("clean", rng)) if args.simulate else read_fn
    baseline = collect_baseline(baseline_read_fn, args.baseline_samples)
    print(f"Baseline set: {baseline}")

    for cycle in range(1, args.cycles + 1):
        if args.simulate:
            _current_profile[0] = rng.choices(["clean", "review", "alert"], weights=[0.5, 0.25, 0.25])[0]
        print(f"\n-- scan cycle {cycle}/{args.cycles} --" + (f" (sim profile={_current_profile[0]})" if args.simulate else ""))
        run_scan(read_fn=read_fn, calibrator=calibrator, baseline=baseline,
                  window_size=args.window_size, classifier=classifier, zone=zone,
                  outputs=outputs, eventlog=eventlog, publisher=publisher,
                  device_id=args.device_id)
        if not args.simulate:
            time.sleep(1.0)

    print("\n-- sync pass: draining anything still queued --")
    pending_before = len(eventlog.pending())
    sent = drain_pending(eventlog, publisher)
    print(f"Drained {sent}/{pending_before} queued events. "
          f"{len(eventlog.pending())} still pending.")


if __name__ == "__main__":
    main()
