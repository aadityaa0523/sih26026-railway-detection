"""
Guided handheld DEMO: sniff -> dummy heat swab -> two-route decision -> alert -> signed-style log.

EVERYTHING SENSOR-SIDE IS SIMULATED (no gas sensor, heater or swab chemistry involved). The "dummy swab"
is a prop: the presenter picks which numbered pad was inserted and the device replays a scripted
curve for it. Say so out loud; the banner and every result line also say SIMULATED.

    python -m handheld.demo_flow                 # interactive: asks which pad (1-4)
    python -m handheld.demo_flow --pad 3 --fast  # non-interactive, no animation delay
    python -m handheld.demo_flow --hardware      # same, but drive the real LEDs/buzzer (Pi only)
"""
import argparse
import random
import time
import warnings
from pathlib import Path

from handheld.alerts import AlertEngine, ZoneConfig
from handheld.calibration import Calibrator
from handheld.classifier import Classifier
from handheld.eventlog import EventLog
from handheld.features import extract_features
from handheld.heat import SimulatedHeatBackend, classify_heat
from handheld.main import _DummyModel, _SimulatedOutputs, load_model, read_simulated
from handheld.routes import fuse_routes

# The checked-in model.joblib was pickled with an older scikit-learn; the warning is noise on stage.
warnings.filterwarnings("ignore", message=".*Trying to unpickle estimator.*")

# pad number -> (what the presenter says it is, sniff profile, heat sample, expected result)
PADS = {
    1: ("Clean pad, bag with nothing on it", "clean", "blank", "CLEAN"),
    2: ("Distractor: sanitiser / perfume on the bag", "review", "sanitiser", "REVIEW (one route only)"),
    3: ("Legal stand-in: dried nail-polish dab (nitrate-ester class)", "alert", "nitro_standin", "ALERT (two routes agree)"),
    4: ("Unfamiliar residue", "clean", "unfamiliar", "REVIEW (unknown, goes to a human)"),
}
BANNER = "=" * 68 + "\n  SIMULATED DEMO -- no real sensor, heater or swab chemistry is used.\n  The pad is a prop; the curve is a scripted replay.\n" + "=" * 68


def _model(path: str):
    try:
        return load_model(path)
    except Exception:
        return _DummyModel()


def run_flow(pad: int, *, fast: bool = True, outputs=None, db_path: str = ":memory:", out=print) -> dict:
    said, sniff_profile, heat_sample, expected = PADS[pad]
    pause = (lambda s: None) if fast else time.sleep
    rng = random.Random(pad)
    out(f"\nPad {pad}: {said}\n")

    out("[1/4] SNIFF  warming up and taking a clean-air baseline...")
    cal = Calibrator()
    base = cal.set_baseline([read_simulated("clean", rng) for _ in range(5)])
    pause(0.8)
    trace = [cal.to_ratio(read_simulated(sniff_profile, rng), base) for _ in range(8)]
    clf = Classifier(_model(str(Path(__file__).with_name("model.joblib"))), reject_threshold=0.75)
    sniff = AlertEngine().evaluate(clf.predict(extract_features(trace)), ZoneConfig(alert_threshold=0.75))
    out(f"      vapour screen -> {sniff.tier.upper()}  (SIMULATED)")

    out("\n[2/4] HEAT   pad inserted, chamber sealed, heating 50 -> 250 C  (SIMULATED)")
    samples = SimulatedHeatBackend(heat_sample, seed=pad).run_ramp()
    top = max(abs(s.no2) for s in samples) or 1.0
    for s in samples[::3]:
        bar = "#" * max(0, int(28 * max(s.no2, 0) / max(top, 0.6)))
        out(f"      {s.temp_c:5.0f} C | NO2 {s.no2:5.2f} | {bar}")
        pause(0.35)
    heat = classify_heat(samples)
    out(f"      NO2 peak {heat.peak:.2f} at {heat.peak_temp_c:.0f} C -> {heat.label}")

    out("\n[3/4] DECIDE  two-route rule")
    decision = fuse_routes(sniff.tier, heat.label)
    out(f"      {decision.tier.upper()}  ({decision.routes_agreeing}/2 routes agree: {decision.reason})")
    fired = (outputs or _SimulatedOutputs()).fire(decision.tier)

    out("\n[4/4] RECORD  logged to the hash-linked event log (signature SIMULATED)")
    rec = EventLog(db_path).record({"device_id": "handheld-demo", "pad": pad, "sniff": sniff.tier, "heat": heat.label,
                                    "tier": decision.tier, "routes_agreeing": decision.routes_agreeing, "simulated": True})
    out(f"      record #{rec.id} saved; queued for sync when online")
    out(f"\nExpected for this pad: {expected}.  Every positive still needs FSL / IMS lab confirmation.")
    return {"pad": pad, "sniff": sniff.tier, "heat": heat.label, "tier": decision.tier, "agree": decision.routes_agreeing, "fired": fired}


def main():
    ap = argparse.ArgumentParser(description="Guided simulated handheld demo")
    ap.add_argument("--pad", type=int, choices=sorted(PADS))
    ap.add_argument("--fast", action="store_true", help="no animation delays")
    ap.add_argument("--hardware", action="store_true", help="drive real LEDs/buzzer (Pi only); sensors stay simulated")
    ap.add_argument("--db-path", default="handheld_demo_events.db")
    a = ap.parse_args()
    print(BANNER)
    pad = a.pad
    if pad is None:
        for k, v in PADS.items():
            print(f"  {k}) {v[0]}")
        pad = int(input("Which pad did you insert (1-4)? ").strip() or "3")
    outputs = None
    if a.hardware:
        from handheld.outputs import AlertOutputs
        outputs = AlertOutputs()
    run_flow(pad, fast=a.fast, outputs=outputs, db_path=a.db_path)


if __name__ == "__main__":
    main()
