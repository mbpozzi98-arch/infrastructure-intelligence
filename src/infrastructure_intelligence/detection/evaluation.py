import polars as pl


def evaluate_detector(results: pl.DataFrame) -> dict[str, float]:
    """Evaluate the performance of an anomaly detector using confusion matrix metrics."""
    confusion = results.select(
        (pl.col("is_anomaly") & pl.col("predicted_anomaly"))
        .sum()
        .alias("true_positives"),
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

    counts = confusion.to_dicts()[0]

    tp = counts["true_positives"]
    fp = counts["false_positives"]
    fn = counts["false_negatives"]
    tn = counts["true_negatives"]

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1_score = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    fp_rate = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1_score,
        "false_positive_rate": fp_rate,
    }
