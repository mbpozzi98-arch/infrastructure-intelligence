import polars as pl


def calculate_cpu_baselines(
    df: pl.DataFrame,
) -> pl.DataFrame:
    """Calculate historical CPU statistics for each server."""

    return (
        df.group_by("server_id")
        .agg(
            pl.col("cpu_pct").mean().alias("cpu_mean"),
            pl.col("cpu_pct").std().alias("cpu_std"),
        )
        .sort("server_id")
    )


def detect_cpu_anomalies(
    evaluation_df: pl.DataFrame,
    baselines: pl.DataFrame,
    threshold: float = 3.0,
) -> pl.DataFrame:
    """Detect unusual CPU utilization using per-server Z-scores."""

    if threshold <= 0:
        raise ValueError("threshold must be positive")

    result = evaluation_df.join(
        baselines,
        on="server_id",
        how="left",
        validate="m:1",
    )

    if result.select(
        pl.any_horizontal(
            pl.col("cpu_mean").is_null(),
            pl.col("cpu_std").is_null(),
            pl.col("cpu_std") <= 0,
            pl.col("cpu_mean").is_nan(),
            pl.col("cpu_std").is_nan(),
        ).any()
    ).item():
        raise ValueError("Missing or invalid CPU baseline statistics")

    result = result.with_columns(
        ((pl.col("cpu_pct") - pl.col("cpu_mean")) / pl.col("cpu_std")).alias(
            "cpu_zscore"
        )
    )

    result = result.with_columns(
        (pl.col("cpu_zscore").abs() > threshold).alias("predicted_anomaly")
    )

    return result
