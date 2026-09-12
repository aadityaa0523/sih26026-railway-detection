"""
Seam under test: extract_features(trace) -> dict[str, float]

A scan is a short trace of ratio-readings (Calibrator.to_ratio() output, sampled repeatedly
over the ~few-second sniff window), not a single number. Per the project's research, raw
per-sample ratios don't separate classes well -- what does is: how high each channel peaked,
how fast it got there, and how channels compare to each other AT that peak (e.g. terpene
signatures skew mq135/mq2 while acetic-acid signatures skew mq3). This module turns a raw
trace into that fixed-shape feature vector for the model, and nothing else.
"""
from handheld.features import extract_features


def test_flat_trace_has_zero_rise_rate_and_peak_equal_to_the_constant_value():
    # Clean air: every channel reads ~baseline the whole window, no peak, no rise.
    trace = [
        {"mq135": 1.0, "mq3": 1.0, "mq2": 1.0},
        {"mq135": 1.0, "mq3": 1.0, "mq2": 1.0},
        {"mq135": 1.0, "mq3": 1.0, "mq2": 1.0},
    ]

    features = extract_features(trace)

    assert features["mq135_peak"] == 1.0
    assert features["mq135_rise_rate"] == 0.0
    assert features["mq3_over_mq135_peak_ratio"] == 1.0


def test_rising_peak_is_captured_by_peak_and_rise_rate_not_the_last_sample():
    # A real sniff: reading climbs to a peak mid-window then starts to fall off as the
    # fan clears the chamber. The peak and rise-rate must reflect that peak, not sample[-1].
    trace = [
        {"mq135": 1.0, "mq3": 1.0},
        {"mq135": 1.2, "mq3": 1.0},
        {"mq135": 1.8, "mq3": 1.0},
        {"mq135": 1.3, "mq3": 1.0},
    ]

    features = extract_features(trace)

    assert features["mq135_peak"] == 1.8
    assert features["mq135_rise_rate"] == (1.8 - 1.0) / 4


def test_cross_channel_ratio_distinguishes_traces_with_identical_single_channel_peaks():
    # Two traces can share the exact same mq3 peak and mq135 peak in isolation, yet only
    # the cross-channel ratio at peak tells them apart -- this is the feature that matters.
    terpene_like = [
        {"mq135": 2.0, "mq3": 1.0},
        {"mq135": 2.0, "mq3": 1.0},
    ]
    acetic_like = [
        {"mq135": 1.0, "mq3": 2.0},
        {"mq135": 1.0, "mq3": 2.0},
    ]

    terpene_features = extract_features(terpene_like)
    acetic_features = extract_features(acetic_like)

    assert terpene_features["mq3_over_mq135_peak_ratio"] == 0.5
    assert acetic_features["mq3_over_mq135_peak_ratio"] == 2.0
