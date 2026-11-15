import polars as pl

from infrastructure_intelligence.data.synthetic import (
    generate_telemetry,
    inject_anomalies,
)
from infrastructure_intelligence.detection.evaluation import (
    evaluate_detector,
)
from infrastructure_intelligence.detection.multivariate import (
    calculate_metric_baselines,
    detect_multivariate_anomalies,
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


# CPU only anomaly detection
baselines = calculate_cpu_baselines(baseline_df)

cpu_results = detect_cpu_anomalies(
    evaluation_df,
    baselines,
    threshold=3.0,
)

cpu_metrics = evaluate_detector(cpu_results)
print("CPU Anomaly Detection Evaluation:")
print(cpu_metrics)


# Multivariate detection using CPU, memory, and temperature metrics
metrics = ["cpu_pct", "memory_pct", "temperature_c"]

# Calculate historical baselines for each server and metric
multivariate_baselines = calculate_metric_baselines(
    baseline_df,
    metrics,
)

# Run the multivariate anomaly detection algorithm on the evaluation data
multivariate_results = detect_multivariate_anomalies(
    evaluation_df,
    multivariate_baselines,
    metrics,
    threshold=3.0,
)

# Evaluate the performance of the multivariate anomaly detector
multivariate_evaluation = evaluate_detector(multivariate_results)

print("\nMultivariate Anomaly Detection Evaluation:")
print(multivariate_evaluation)


false_negatives = multivariate_results.filter(
    pl.col("is_anomaly") & ~pl.col("predicted_anomaly")
)

print(
    false_negatives.select(
        "server_id",
        "anomaly_type",
        "cpu_pct",
        "memory_pct",
        "temperature_c",
        "cpu_pct_zscore",
        "memory_pct_zscore",
        "temperature_c_zscore",
    )
)
