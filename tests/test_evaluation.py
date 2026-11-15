import polars as pl
import pytest

from infrastructure_intelligence.detection.evaluation import (
    evaluate_detector,
)


def test_evaluate_detector():
    # Create a sample DataFrame with true labels and predicted labels with 2 TP, 1 FP, 1 FN, and 6 TN
    df = pl.DataFrame(
        {
            "is_anomaly": [
                True,
                True,
                False,
                True,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
            "predicted_anomaly": [
                True,
                True,
                True,
                False,
                False,
                False,
                False,
                False,
                False,
                False,
            ],
        }
    )

    metrics = evaluate_detector(df)

    assert metrics["precision"] == pytest.approx(2 / 3)
    assert metrics["recall"] == pytest.approx(2 / 3)
    assert metrics["f1"] == pytest.approx(2 / 3)
    assert metrics["false_positive_rate"] == pytest.approx(1 / 7)
