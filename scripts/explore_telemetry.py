import polars as pl

from infrastructure_intelligence.data.synthetic import (
    generate_telemetry,
    inject_anomalies,
)
from infrastructure_intelligence.detection.statistical import (
    calculate_cpu_baselines,
    detect_cpu_anomalies,
)

normal_df = generate_telemetry(
    n_servers=3,
    n_hours=336,
    seed=42,
)

cutoff = normal_df["timestamp"].min() + __import__("datetime").timedelta(days=7)

baseline_df = normal_df.filter(pl.col("timestamp") < cutoff)

evaluation_df = normal_df.filter(pl.col("timestamp") >= cutoff)

evaluation_df = inject_anomalies(
    evaluation_df,
    anomaly_fraction=0.05,
    seed=42,
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
        "timestamp",
        "cpu_pct",
        "cpu_zscore",
        "is_anomaly",
        "anomaly_type",
        "predicted_anomaly",
    ).filter(pl.col("predicted_anomaly"))
)

confusion = results.select(
    (pl.col("is_anomaly") & pl.col("predicted_anomaly")).sum().alias("true_positives"),
    (~pl.col("is_anomaly") & pl.col("predicted_anomaly"))
    .sum()
    .alias("false_positives"),
    (pl.col("is_anomaly") & ~pl.col("predicted_anomaly"))
    .sum()
    .alias("false_negatives"),
    (~pl.col("is_anomaly") & ~pl.col("predicted_anomaly"))
    .sum()
    .alias("true_negatives"),
)

print(confusion)

performance_by_type = (
    results.filter(pl.col("is_anomaly"))
    .group_by("anomaly_type")
    .agg(
        pl.len().alias("total_anomalies"),
        pl.col("predicted_anomaly").sum().alias("detected"),
    )
    .with_columns((pl.col("detected") / pl.col("total_anomalies")).alias("recall"))
    .sort("anomaly_type")
)

print(performance_by_type)

performance_by_server = (
    results.group_by("server_id")
    .agg(
        pl.col("is_anomaly").sum().alias("actual_anomalies"),
        pl.col("predicted_anomaly").sum().alias("alerts"),
        (pl.col("is_anomaly") & pl.col("predicted_anomaly"))
        .sum()
        .alias("true_positives"),
    )
    .sort("server_id")
)

print(performance_by_server)
