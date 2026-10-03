"""
Swab demo: runs one HEAT cycle and the two-route decision, entirely SIMULATED, and saves a
plot stamped "SIMULATED, NOT MEASURED".

    python -m handheld.swab_demo --sample nitro_standin --sniff alert
    python -m handheld.swab_demo --all          # every sample, prints a summary table

This shows the flow and the decision logic. It is not evidence the device detects anything;
real evidence is the bench test with the real chamber (see FEASIBILITY_REPORT 3.1).
"""
import argparse
from pathlib import Path

from handheld.heat import SIM_PROFILES, SimulatedHeatBackend, classify_heat
from handheld.routes import fuse_routes

BANNER = "=" * 66 + "\n  SIMULATED DATA -- no sensor, no heater, no swab. DEMO OF THE FLOW ONLY.\n" + "=" * 66


def run(sample: str, sniff: str, seed: int):
    samples = SimulatedHeatBackend(sample, seed).run_ramp()
    heat = classify_heat(samples)
    decision = fuse_routes(sniff, heat.label)
    return samples, heat, decision


def plot(samples, title: str, path: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot([s.temp_c for s in samples], [s.no2 for s in samples], lw=2)
    ax.set_xlabel("chamber temperature (C)")
    ax.set_ylabel("NO2 response (ppm-equiv)")
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.text(0.5, 0.5, "SIMULATED, NOT MEASURED", transform=ax.transAxes, ha="center", va="center",
            fontsize=26, color="red", alpha=0.25, rotation=20, weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sample", default="nitro_standin", choices=sorted(SIM_PROFILES))
    p.add_argument("--sniff", default="clean", choices=["clean", "review", "alert"])
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--all", action="store_true")
    p.add_argument("--plot", type=Path, default=None, help="save the NO2-vs-temperature plot here")
    a = p.parse_args()
    print(BANNER)
    if a.all:
        print(f"{'sample':14s} {'peak':>6s} {'T_peak':>7s}  heat label     tier (sniff={a.sniff})")
        for name in SIM_PROFILES:
            _, h, d = run(name, a.sniff, a.seed)
            print(f"{name:14s} {h.peak:6.2f} {h.peak_temp_c:6.0f}C  {h.label:13s}  {d.tier} ({d.routes_agreeing}/2: {d.reason})")
        return
    samples, h, d = run(a.sample, a.sniff, a.seed)
    print(f"sample={a.sample}  sniff route={a.sniff}")
    print(f"HEAT: {h.label} (conf {h.confidence:.2f}), NO2 peak {h.peak:.2f} at {h.peak_temp_c:.0f} C")
    print(f"DECISION: {d.tier.upper()}  routes agreeing {d.routes_agreeing}/2 -- {d.reason}")
    if a.plot:
        plot(samples, f"HEAT ramp: {a.sample}", a.plot)
        print("plot saved to", a.plot)


if __name__ == "__main__":
    main()
