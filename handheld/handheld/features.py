"""
extract_features: turns a raw scan trace into the fixed-shape vector the model trains on.

A single ratio-reading isn't enough to separate classes -- per the project's research, what
actually carries signal is how high each channel peaked over the sniff window, how fast it
got there (rise-rate), and how channels compare to each other AT that peak (cross-channel
ratio). A terpene-heavy hit and an acetic-acid-heavy hit can have the same mq135 peak in
isolation; only the ratio between channels tells them apart.
"""
from itertools import permutations


def extract_features(trace: list[dict[str, float]]) -> dict[str, float]:
    channels = sorted(trace[0].keys())
    peaks = {channel: max(sample[channel] for sample in trace) for channel in channels}
    firsts = {channel: trace[0][channel] for channel in channels}

    features: dict[str, float] = {}
    for channel in channels:
        features[f"{channel}_peak"] = peaks[channel]
        features[f"{channel}_rise_rate"] = (peaks[channel] - firsts[channel]) / len(trace)

    for a, b in permutations(channels, 2):
        ratio = peaks[a] / peaks[b] if peaks[b] != 0 else 0.0
        features[f"{a}_over_{b}_peak_ratio"] = ratio

    return features
