"""
RandomForestModel: adapts sklearn's RandomForestClassifier to the ProbabilityModel Protocol
that classifier.py already depends on (dict-in, dict-out).

Classifier must never know sklearn exists -- it only calls .predict_proba(features) -> dict.
That indirection is what lets train.py swap the algorithm later (SVM, gradient boosting)
without touching the decision logic in classifier.py or alerts.py.
"""
import joblib
from sklearn.ensemble import RandomForestClassifier


def load_model(path: str) -> "RandomForestModel":
    """Loads a RandomForestModel saved by train.py's joblib.dump(). Raises FileNotFoundError
    (via joblib/pickle's own open()) if path doesn't exist -- callers rely on that to fall
    back to a heuristic stub when no trained model is present yet."""
    return joblib.load(path)


class RandomForestModel:
    def __init__(self, **kwargs):
        self._classifier = RandomForestClassifier(**kwargs)
        self._feature_names: list[str] = []

    def fit(self, features: list[dict[str, float]], labels: list[str]) -> None:
        self._feature_names = sorted({name for sample in features for name in sample})
        rows = [[sample.get(name, 0.0) for name in self._feature_names] for sample in features]
        self._classifier.fit(rows, labels)

    def predict_proba(self, features: dict[str, float]) -> dict[str, float]:
        row = [[features.get(name, 0.0) for name in self._feature_names]]
        probabilities = self._classifier.predict_proba(row)[0]
        return {str(label): float(p) for label, p in zip(self._classifier.classes_, probabilities)}
