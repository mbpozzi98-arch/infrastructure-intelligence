import polars as pl
import pytest

from infrastructure_intelligence.detection.statistical import (
    calculate_cpu_baselines,
    detect_cpu_anomalies,
)


def test_calculate_cpu_baselines():
    df = pl.DataFrame(
        {
            "server_id": [
                "srv-001",
                "srv-001",
                "srv-002",
                "srv-002",
            ],
            "cpu_pct": [40.0, 60.0, 70.0, 90.0],
        }
    )

    result = calculate_cpu_baselines(df)

    assert result.height == 2

    server_1 = result.filter(pl.col("server_id") == "srv-001")

    assert server_1["cpu_mean"].item() == pytest.approx(50.0)
    assert server_1["cpu_std"].item() == pytest.approx(14.1421356)


def test_detect_cpu_spike():
    baseline_df = pl.DataFrame(
        {
            "server_id": ["srv-001"] * 3,
            "cpu_pct": [30.0, 35.0, 40.0],
        }
    )

    evaluation_df = pl.DataFrame(
        {
            "server_id": ["srv-001", "srv-001"],
            "cpu_pct": [35.0, 85.0],
        }
    )

    baselines = calculate_cpu_baselines(baseline_df)

    result = detect_cpu_anomalies(
        evaluation_df,
        baselines,
        threshold=3.0,
    )

    assert result["predicted_anomaly"].to_list() == [
        False,
        True,
    ]


def test_missing_server_baseline():
    baseline_df = pl.DataFrame(
        {
            "server_id": ["srv-001", "srv-001"],
            "cpu_pct": [30.0, 40.0],
        }
    )

    evaluation_df = pl.DataFrame(
        {
            "server_id": ["srv-002"],
            "cpu_pct": [85.0],
        }
    )

    baselines = calculate_cpu_baselines(baseline_df)

    with pytest.raises(ValueError):
        detect_cpu_anomalies(
            evaluation_df,
            baselines,
        )
