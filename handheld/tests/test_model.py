"""
Seam under test: RandomForestModel.predict_proba(features) -> dict[str, float]

RandomForestModel exists so Classifier (classifier.py) never has to know sklearn exists --
it only depends on the ProbabilityModel Protocol (.predict_proba(dict) -> dict). These tests
prove the adapter's dict-in/dict-out shape is correct on trivially separable synthetic data.
Real-world accuracy is NOT this seam's job -- that needs real sensor data (see train.py).
"""
from handheld.model import RandomForestModel


def _fit_on_trivially_separable_data() -> RandomForestModel:
    model = RandomForestModel(n_estimators=10, random_state=0)
    features = [
        {"mq135_peak": 0.1, "mq3_peak": 0.1},
        {"mq135_peak": 0.2, "mq3_peak": 0.1},
        {"mq135_peak": 5.0, "mq3_peak": 5.0},
        {"mq135_peak": 5.2, "mq3_peak": 4.9},
    ]
    labels = ["clean", "clean", "terpene_cannabis", "terpene_cannabis"]
    model.fit(features, labels)
    return model


def test_predict_proba_returns_a_probability_per_trained_class():
    model = _fit_on_trivially_separable_data()

    probabilities = model.predict_proba({"mq135_peak": 5.1, "mq3_peak": 5.0})

    assert set(probabilities.keys()) == {"clean", "terpene_cannabis"}
    assert abs(sum(probabilities.values()) - 1.0) < 1e-9


def test_predict_proba_favours_the_correct_class_on_clearly_separable_input():
    model = _fit_on_trivially_separable_data()

    clean_probabilities = model.predict_proba({"mq135_peak": 0.15, "mq3_peak": 0.1})
    positive_probabilities = model.predict_proba({"mq135_peak": 5.1, "mq3_peak": 5.0})

    assert clean_probabilities["clean"] > clean_probabilities["terpene_cannabis"]
    assert positive_probabilities["terpene_cannabis"] > positive_probabilities["clean"]
