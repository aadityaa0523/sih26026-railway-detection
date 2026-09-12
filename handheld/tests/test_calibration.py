"""
Seam under test: Calibrator.set_baseline() / .to_ratio()

MQ sensors drift with temperature/humidity/sensor age -- the only honest way to read them
is relative to a fresh clean-air baseline taken just before each scan, not an absolute
voltage. These tests verify that arithmetic, not the real ADC/I2C hardware.
"""
from handheld.calibration import Calibrator


def test_baseline_is_the_average_of_clean_air_readings_per_channel():
    calibrator = Calibrator()
    clean_air_samples = [
        {"mq135": 100.0, "mq3": 200.0},
        {"mq135": 102.0, "mq3": 198.0},
        {"mq135": 98.0, "mq3": 202.0},
    ]

    baseline = calibrator.set_baseline(clean_air_samples)

    assert baseline == {"mq135": 100.0, "mq3": 200.0}


def test_ratio_is_reading_divided_by_that_channels_baseline():
    calibrator = Calibrator()
    baseline = {"mq135": 100.0, "mq3": 200.0}

    ratio = calibrator.to_ratio(reading={"mq135": 150.0, "mq3": 190.0}, baseline=baseline)

    assert ratio == {"mq135": 1.5, "mq3": 0.95}
