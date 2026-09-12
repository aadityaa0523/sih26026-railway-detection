"""
Seam under test: Classifier.predict(features) -> ClassificationResult

Classifier wraps an injected model (anything with .predict_proba(features) -> dict[label, float])
and applies the confidence-threshold + rejection policy. The model's own real-world accuracy is
NOT what these tests verify (that needs real sensor data, tracked separately) -- these tests verify
the decision logic: given a model's probabilities, does the classifier pick the right label, and
does it correctly refuse to guess when nothing is confident enough?
"""
from handheld.classifier import Classifier, ClassificationResult


class StubModel:
    """A fake model: hand a fixed probability dict, get it back verbatim."""

    def __init__(self, probabilities: dict[str, float]):
        self._probabilities = probabilities

    def predict_proba(self, features: dict[str, float]) -> dict[str, float]:
        return self._probabilities


def test_predicts_the_highest_confidence_class():
    model = StubModel({"terpene_cannabis": 0.91, "acetic_heroin": 0.05, "clean": 0.04})
    classifier = Classifier(model=model, reject_threshold=0.6)

    result = classifier.predict(features={})

    assert result == ClassificationResult(label="terpene_cannabis", confidence=0.91, is_unknown=False)


def test_flags_unknown_when_no_class_clears_the_reject_threshold():
    # e.g. perfume: doesn't cleanly match any trained class -- this is the behaviour that
    # keeps a false-alarm-prone sensor honest instead of forcing a guess.
    model = StubModel({"terpene_cannabis": 0.35, "acetic_heroin": 0.30, "clean": 0.35})
    classifier = Classifier(model=model, reject_threshold=0.6)

    result = classifier.predict(features={})

    assert result.is_unknown is True
    assert result.label == "unknown"
