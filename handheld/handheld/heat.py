"""
HEAT route: heat a swab 50 -> 250 C in a small chamber and watch an NO2 sensor for gas
released at a particular temperature (nitro / nitrate-ester residues give NO2 when they
decompose). See RAIL-N.E.D._FEASIBILITY_REPORT.md section 3.1.

The sensor side is swappable:
  * SimulatedHeatBackend -- NO hardware. Synthetic curves for a nitrate-ester STAND-IN and a
    few distractors. Everything it produces is SIMULATED and must be labelled as such.
  * HardwareHeatBackend  -- MAX6675 thermocouple + MCH heater (PWM via MOSFET) + any NO2
    sensor you pass in as a callable. UNTESTED on real hardware (no hardware built yet).

A ramp returns list[HeatSample]; extract_heat_features() and classify_heat() turn it into a
decision. classify_heat is a plain threshold rule, NOT a trained model -- the thresholds are
placeholders until the bench test (nail-polish stand-in vs distractors) sets real ones.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

RAMP_START_C = 50.0
RAMP_END_C = 250.0
HARD_CUTOFF_C = 260.0      # software cut-off; the thermal fuse is the hardware backup
SAMPLE_PERIOD_S = 1.0
RAMP_SECONDS = 30


@dataclass(frozen=True)
class HeatSample:
    t_s: float
    temp_c: float
    no2: float          # sensor response in ppm-equivalent units (can dip below 0 with drift)


@dataclass(frozen=True)
class HeatResult:
    label: str          # "nitro_class" | "unknown" | "clean"
    confidence: float
    peak: float
    peak_temp_c: float


# --- backends -------------------------------------------------------------------------

# name -> list of (centre_C, width_C, amplitude) gaussian bumps. Amplitudes are made up for
# the demo: the stand-in gives a clear positive NO2 peak near 185 C, distractors give small or
# negative (reducing-gas) responses elsewhere.
SIM_PROFILES: dict[str, list[tuple[float, float, float]]] = {
    "blank": [],
    "nitro_standin": [(185.0, 14.0, 1.2)],
    "vinegar": [(95.0, 18.0, -0.15)],
    "coffee": [(150.0, 25.0, -0.2), (210.0, 20.0, 0.08)],
    "diesel": [(120.0, 22.0, -0.25)],
    "sanitiser": [(80.0, 15.0, -0.2)],
    "unfamiliar": [(130.0, 18.0, 0.35)],     # something responds, but not the nitro signature -> "unknown"
}


class SimulatedHeatBackend:
    SIMULATED = True

    def __init__(self, sample: str = "blank", seed: int | None = None):
        if sample not in SIM_PROFILES:
            raise ValueError(f"unknown simulated sample {sample!r}; choose from {sorted(SIM_PROFILES)}")
        self.sample = sample
        self._rng = random.Random(seed)

    def run_ramp(self) -> list[HeatSample]:
        out = []
        n = int(RAMP_SECONDS / SAMPLE_PERIOD_S) + 1
        for i in range(n):
            temp = RAMP_START_C + (RAMP_END_C - RAMP_START_C) * i / (n - 1)
            signal = 0.05 + 0.0002 * (temp - RAMP_START_C)           # slow baseline drift
            for centre, width, amp in SIM_PROFILES[self.sample]:
                signal += amp * math.exp(-((temp - centre) ** 2) / (2 * width ** 2))
            signal += self._rng.gauss(0, 0.02)
            out.append(HeatSample(i * SAMPLE_PERIOD_S, temp, signal))
        return out


class HardwareHeatBackend:
    """Real chamber. UNTESTED. read_no2 is any callable returning the NO2 reading (ppm-equiv),
    so the MiCS-2714 / Grove NO2 / electrochemical module can be swapped without touching this.
    The NO2 sensor must sit DOWNSTREAM of the chamber, cool, fed by the pump -- never inside
    the 250 C space."""

    SIMULATED = False

    def __init__(self, read_no2, heater_pin: int = 12, spi_bus: int = 0, spi_dev: int = 1):
        try:
            import spidev
            from gpiozero import PWMOutputDevice
        except ImportError as e:
            raise ImportError("spidev + gpiozero required (Pi only); use SimulatedHeatBackend elsewhere") from e
        self._read_no2 = read_no2
        self._spi = spidev.SpiDev()
        self._spi.open(spi_bus, spi_dev)
        self._spi.max_speed_hz = 4_000_000
        self._heater = PWMOutputDevice(heater_pin, frequency=10)
        self._heater.off()

    def _read_temp_c(self) -> float:
        hi, lo = self._spi.readbytes(2)
        raw = (hi << 8) | lo
        if raw & 0x4:
            raise RuntimeError("MAX6675: thermocouple open circuit")
        return (raw >> 3) * 0.25

    def run_ramp(self) -> list[HeatSample]:
        import time
        out, integral = [], 0.0
        t0 = time.monotonic()
        try:
            while True:
                t = time.monotonic() - t0
                if t > RAMP_SECONDS + 5:
                    break
                temp = self._read_temp_c()
                if temp >= HARD_CUTOFF_C:
                    raise RuntimeError(f"over-temperature {temp:.0f} C, heater off")
                target = RAMP_START_C + (RAMP_END_C - RAMP_START_C) * min(t / RAMP_SECONDS, 1.0)
                err = target - temp
                integral = max(-50.0, min(50.0, integral + err * SAMPLE_PERIOD_S))
                duty = max(0.0, min(1.0, 0.04 * err + 0.002 * integral))
                self._heater.value = duty
                out.append(HeatSample(t, temp, self._read_no2()))
                time.sleep(SAMPLE_PERIOD_S)
        finally:
            self._heater.off()
        return out


# --- features + decision --------------------------------------------------------------

def extract_heat_features(samples: list[HeatSample]) -> dict[str, float]:
    base = sum(s.no2 for s in samples[:4]) / 4
    corrected = [s.no2 - base for s in samples]
    i = max(range(len(samples)), key=lambda k: corrected[k])
    return {"peak": corrected[i], "peak_temp_c": samples[i].temp_c,
            "area": sum(max(c, 0.0) for c in corrected) * SAMPLE_PERIOD_S}


def classify_heat(samples: list[HeatSample]) -> HeatResult:
    f = extract_heat_features(samples)
    peak, temp = f["peak"], f["peak_temp_c"]
    if peak >= 0.5 and 150.0 <= temp <= 230.0:
        return HeatResult("nitro_class", min(0.95, 0.6 + 0.25 * peak), peak, temp)
    if peak >= 0.25:
        return HeatResult("unknown", 0.5, peak, temp)       # something responded, not our signature
    return HeatResult("clean", 0.9, peak, temp)
