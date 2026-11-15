import polars as pl
import pytest

from infrastructure_intelligence.detection.multivariate import (
    calculate_metric_baselines,
    detect_multivariate_anomalies,
)


def test_calculate_metric_baselines():
    df = pl.DataFrame(
        {
            "server_id": [
                "srv-001",
                "srv-001",
                "srv-002",
                "srv-002",
            ],
            "cpu_pct": [40.0, 60.0, 70.0, 90.0],
            "memory_pct": [50.0, 70.0, 60.0, 80.0],
            "temperature_c": [45.0, 55.0, 65.0, 75.0],
        }
    )

    result = calculate_metric_baselines(
        df,
        metrics=["cpu_pct", "memory_pct", "temperature_c"],
    )

    assert result.height == 2

    server_1 = result.filter(pl.col("server_id") == "srv-001")

    assert server_1["cpu_pct_mean"].item() == pytest.approx(50.0)
    assert server_1["memory_pct_mean"].item() == pytest.approx(60.0)
    assert server_1["temperature_c_mean"].item() == pytest.approx(50.0)
    assert server_1["cpu_pct_std"].item() == pytest.approx(200**0.5)


def test_detect_multivariate_anomalies():
    baseline_df = pl.DataFrame(
        {
            "server_id": ["srv-001"] * 3,
            "cpu_pct": [30.0, 35.0, 40.0],
            "memory_pct": [40.0, 45.0, 50.0],
            "temperature_c": [45.0, 50.0, 55.0],
        }
    )

    evaluation_df = pl.DataFrame(
        {
            "server_id": ["srv-001"] * 4,
            "cpu_pct": [35.0, 85.0, 35.0, 35.0],
            "memory_pct": [45.0, 45.0, 90.0, 45.0],
            "temperature_c": [50.0, 50.0, 50.0, 80.0],
        }
    )

    metrics = ["cpu_pct", "memory_pct", "temperature_c"]

    baselines = calculate_metric_baselines(
        baseline_df,
        metrics,
    )

    result = detect_multivariate_anomalies(
        evaluation_df,
        baselines,
        metrics,
        threshold=3.0,
    )

    assert result["predicted_anomaly"].to_list() == [
        False,  # Normal observation
        True,  # CPU spike
        True,  # Memory pressure
        True,  # Overheating
    ]
