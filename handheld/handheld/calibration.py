"""
Calibrator: turns raw sensor voltages into baseline-relative ratios.

MQ sensors drift with temperature/humidity/age -- an absolute voltage means nothing on its
own. Every scan is read relative to a clean-air baseline taken immediately before it.
"""
from statistics import mean


class Calibrator:
    def set_baseline(self, clean_air_samples: list[dict[str, float]]) -> dict[str, float]:
        channels = clean_air_samples[0].keys()
        return {channel: mean(sample[channel] for sample in clean_air_samples) for channel in channels}

    def to_ratio(self, reading: dict[str, float], baseline: dict[str, float]) -> dict[str, float]:
        return {channel: value / baseline[channel] for channel, value in reading.items()}
