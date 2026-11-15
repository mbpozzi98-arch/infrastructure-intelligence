from infrastructure_intelligence.data.synthetic import (
    generate_telemetry,
    inject_anomalies,
)
import polars as pl


def test_expected_observation_count():
    df = generate_telemetry(
        n_servers=3,
        n_hours=168,
    )

    assert len(df) == 504
    assert df["server_id"].n_unique() == 3


def test_cpu_utilization_bounds():
    df = generate_telemetry()

    assert df.select(pl.col("cpu_pct").is_between(0, 100).all()).item()


def test_no_duplicate_observations():
    df = generate_telemetry()

    duplicates = df.select(["server_id", "timestamp"]).is_duplicated()

    assert not duplicates.any()


def test_anomaly_injection_preserves_row_count():
    normal_df = generate_telemetry(
        n_servers=3,
        n_hours=100,
    )

    anomalous_df = inject_anomalies(
        normal_df,
        anomaly_fraction=0.05,
    )

    assert anomalous_df.height == normal_df.height
    assert anomalous_df["is_anomaly"].sum() == 15


def test_anomaly_injection_is_reproducible():
    df = generate_telemetry()

    result_1 = inject_anomalies(df, seed=42)
    result_2 = inject_anomalies(df, seed=42)

    assert result_1.equals(result_2)
