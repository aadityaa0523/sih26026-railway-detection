"""
train.py -- trains RandomForestModel on SYNTHETIC sensor traces and saves handheld/model.joblib.

*** SYNTHETIC DATA -- this is placeholder training data for architecture validation only. ***
*** Replace with real sensor recordings (25+ samples/class per the project's data-collection ***
*** plan) before any real demo or accuracy claim. The numbers this script prints are NOT a   ***
*** measure of real-world detection accuracy -- they only prove the features/model/save      ***
*** pipeline runs end to end.                                                                ***

Class ratio ranges below are placeholder guesses (per session.md's marker-VOC research: terpenes
skew mq135/mq2, acetic acid skews mq3) -- not measurements from a real MQ-3/MQ-135/MQ-2 array.
"""
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from handheld.features import extract_features
from handheld.model import RandomForestModel

SYNTHETIC_DATA_WARNING = (
    "\n"
    "==================== SYNTHETIC DATA -- NOT REAL SENSOR READINGS ====================\n"
    "This script trains on placeholder data for architecture validation only.\n"
    "Replace with real sensor recordings (25+ samples/class per the project's\n"
    "data-collection plan) before any real demo or accuracy claim.\n"
    "The confusion matrix and accuracy below describe how well the pipeline runs,\n"
    "not how well this device detects anything in the real world.\n"
    "======================================================================================\n"
)

# Peak ratio ranges (min, max) per channel per class. Placeholder guesses, not measurements.
CLASS_PEAK_RANGES = {
    "clean": {"mq135": (0.95, 1.05), "mq3": (0.95, 1.05), "mq2": (0.95, 1.05)},
    "terpene_cannabis": {"mq135": (2.5, 4.0), "mq3": (1.1, 1.4), "mq2": (2.2, 3.5)},
    "acetic_heroin": {"mq135": (1.1, 1.4), "mq3": (2.5, 4.0), "mq2": (1.0, 1.3)},
    "perfume": {"mq135": (1.3, 1.8), "mq3": (1.5, 2.0), "mq2": (1.1, 1.4)},
    "sanitizer": {"mq135": (1.0, 1.2), "mq3": (1.8, 2.4), "mq2": (0.95, 1.1)},
    "coffee": {"mq135": (1.6, 2.2), "mq3": (1.0, 1.3), "mq2": (1.3, 1.7)},
}
SAMPLES_PER_CLASS = 60
TRACE_LENGTH = 8
NOISE_STD = 0.03


def generate_trace(rng: np.random.Generator, peak_ranges: dict[str, tuple[float, float]]) -> list[dict[str, float]]:
    """One simulated sniff window: each channel rises from baseline to a random peak within
    its class range, then decays -- shaped like a real MQ-sensor response to a sample pulled
    past the fan, not a real recording."""
    peaks = {channel: rng.uniform(lo, hi) for channel, (lo, hi) in peak_ranges.items()}
    peak_index = rng.integers(2, TRACE_LENGTH - 1)
    trace = []
    for i in range(TRACE_LENGTH):
        sample = {}
        for channel, peak in peaks.items():
            frac = i / peak_index if i <= peak_index else max(0.0, 1 - (i - peak_index) / (TRACE_LENGTH - peak_index))
            value = 1.0 + (peak - 1.0) * frac + rng.normal(0, NOISE_STD)
            sample[channel] = max(value, 0.01)
        trace.append(sample)
    return trace


def generate_dataset(rng: np.random.Generator) -> tuple[list[dict[str, float]], list[str]]:
    features, labels = [], []
    for label, peak_ranges in CLASS_PEAK_RANGES.items():
        for _ in range(SAMPLES_PER_CLASS):
            trace = generate_trace(rng, peak_ranges)
            features.append(extract_features(trace))
            labels.append(label)
    return features, labels


def print_confusion_matrix(y_test: list[str], y_pred: list[str], class_labels: list[str]) -> None:
    matrix = confusion_matrix(y_test, y_pred, labels=class_labels)
    header = "actual \\ predicted".ljust(20) + "".join(label[:10].rjust(12) for label in class_labels)
    print(header)
    for label, row in zip(class_labels, matrix):
        print(label.ljust(20) + "".join(str(count).rjust(12) for count in row))


def main() -> None:
    print(SYNTHETIC_DATA_WARNING)

    rng = np.random.default_rng(42)
    features, labels = generate_dataset(rng)
    class_labels = sorted(CLASS_PEAK_RANGES.keys())

    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.3, random_state=42, stratify=labels
    )

    model = RandomForestModel(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = [max(model.predict_proba(sample).items(), key=lambda item: item[1])[0] for sample in X_test]

    print_confusion_matrix(y_test, y_pred, class_labels)
    print(f"\naccuracy on synthetic held-out split: {accuracy_score(y_test, y_pred):.2f}")

    output_path = Path(__file__).resolve().parent / "model.joblib"
    joblib.dump(model, output_path)
    print(f"\nsaved model to {output_path}")

    print(SYNTHETIC_DATA_WARNING)


if __name__ == "__main__":
    main()
