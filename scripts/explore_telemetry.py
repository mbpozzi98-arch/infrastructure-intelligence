import polars as pl

from infrastructure_intelligence.data.synthetic import (
    generate_telemetry,
    inject_anomalies,
)

normal_df = generate_telemetry(
    n_servers=3,
    n_hours=168,
    seed=42,
)

anomalous_df = inject_anomalies(
    normal_df,
    anomaly_fraction=0.05,
    seed=42,
)

comparison = normal_df.join(
    anomalous_df,
    on=["server_id", "timestamp"],
    suffix="_after",
)

print(
    comparison.filter(pl.col("is_anomaly")).select(
        "server_id",
        "timestamp",
        "anomaly_type",
        "cpu_pct",
        "cpu_pct_after",
        "memory_pct",
        "memory_pct_after",
        "temperature_c",
        "temperature_c_after",
    )
)
