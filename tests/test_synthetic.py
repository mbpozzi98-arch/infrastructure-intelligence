from infrastructure_intelligence.data.synthetic import (
    generate_telemetry,
)


def test_expected_observation_count():
    df = generate_telemetry(
        n_servers=3,
        n_hours=168,
    )

    assert len(df) == 504
    assert df["server_id"].nunique() == 3


def test_cpu_utilization_bounds():
    df = generate_telemetry()

    assert df["cpu_pct"].between(0, 100).all()


def test_no_duplicate_observations():
    df = generate_telemetry()

    duplicates = df.duplicated(subset=["server_id", "timestamp"])

    assert not duplicates.any()
