import pytest

from handheld.heat import SIM_PROFILES, SimulatedHeatBackend, classify_heat
from handheld.routes import fuse_routes


def _heat(sample, seed=1):
    return classify_heat(SimulatedHeatBackend(sample, seed).run_ramp())


def test_standin_is_flagged_in_the_expected_temperature_band():
    r = _heat("nitro_standin")
    assert r.label == "nitro_class"
    assert 150 <= r.peak_temp_c <= 230


@pytest.mark.parametrize("sample", ["blank", "vinegar", "coffee", "diesel", "sanitiser"])
def test_distractors_are_never_flagged_across_seeds(sample):
    for seed in range(20):
        assert _heat(sample, seed).label != "nitro_class"


def test_unknown_sample_name_is_rejected():
    with pytest.raises(ValueError):
        SimulatedHeatBackend("real_rdx")


def test_ramp_covers_50_to_250_c():
    s = SimulatedHeatBackend("blank", 0).run_ramp()
    assert s[0].temp_c == 50.0 and s[-1].temp_c == 250.0


def test_two_route_rule():
    assert fuse_routes("alert", "nitro_class").tier == "alert"
    assert fuse_routes("review", "nitro_class").routes_agreeing == 2
    assert fuse_routes("clean", "nitro_class").tier == "review"     # one route alone never alerts
    assert fuse_routes("alert", "clean").tier == "review"
    assert fuse_routes("clean", "clean").tier == "clean"


def test_demo_flow_pads_give_the_expected_decisions():
    from handheld.demo_flow import run_flow
    quiet = lambda *_a, **_k: None
    r = {p: run_flow(p, fast=True, out=quiet) for p in (1, 2, 3, 4)}
    assert r[1]["tier"] == "clean"
    assert r[2]["tier"] == "review" and r[2]["agree"] == 1      # distractor: one route only
    assert r[3]["tier"] == "alert" and r[3]["agree"] == 2       # stand-in: two routes agree
    assert r[4]["tier"] == "review" and r[4]["heat"] == "unknown"
