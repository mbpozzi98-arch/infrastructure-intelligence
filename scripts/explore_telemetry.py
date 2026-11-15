import polars as pl

from infrastructure_intelligence.detection.statistical import (
    calculate_cpu_baselines,
    detect_cpu_anomalies,
)

baseline_df = pl.DataFrame(
    {
        "server_id": ["srv-001", "srv-001", "srv-001"],
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

results = detect_cpu_anomalies(
    evaluation_df,
    baselines,
    threshold=3.0,
)

print(
    results.select(
        "server_id",
        "cpu_pct",
        "cpu_zscore",
        "predicted_anomaly",
    )
)
