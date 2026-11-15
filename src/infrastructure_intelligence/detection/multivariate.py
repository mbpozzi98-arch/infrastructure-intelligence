import polars as pl


def calculate_metric_baselines(
    df: pl.DataFrame,
    metrics: list[str],
) -> pl.DataFrame:
    """Calculate per-server historical statistics for multiple metrics."""

    agg_exprs = []
    for metric in metrics:
        agg_exprs.append(pl.col(metric).mean().alias(f"{metric}_mean"))
        agg_exprs.append(pl.col(metric).std().alias(f"{metric}_std"))

    return df.group_by("server_id").agg(agg_exprs).sort("server_id")


def detect_multivariate_anomalies(
    evaluation_df: pl.DataFrame,
    baselines: pl.DataFrame,
    metrics: list[str],
    threshold: float = 3.0,
) -> pl.DataFrame:
    """Detect anomalies across multiple metrics using Z-scores."""

    if threshold <= 0:
        raise ValueError("threshold must be positive")
    if not metrics:
        raise ValueError("metrics list cannot be empty")

    result = evaluation_df.join(
        baselines,
        on="server_id",
        how="left",
        validate="m:1",
    )

    zscore_exprs = []
    for metric in metrics:
        mean_col = f"{metric}_mean"
        std_col = f"{metric}_std"
        zscore_col = f"{metric}_zscore"

        if result.select(
            pl.any_horizontal(
                pl.col(mean_col).is_null(),
                pl.col(std_col).is_null(),
                pl.col(std_col) <= 0,
                pl.col(mean_col).is_nan(),
                pl.col(std_col).is_nan(),
            ).any()
        ).item():
            raise ValueError(f"Missing or invalid baseline statistics for {metric}")

        zscore_exprs.append(
            ((pl.col(metric) - pl.col(mean_col)) / pl.col(std_col)).alias(zscore_col)
        )

    result = result.with_columns(zscore_exprs)

    conditions = []
    for metric in metrics:
        zscore_col = f"{metric}_zscore"
        conditions.append(pl.col(zscore_col).abs() > threshold)

    result = result.with_columns(
        pl.any_horizontal(conditions).alias("predicted_anomaly")
    )

    return result
