from datetime import datetime, timedelta, timezone

import numpy as np
import polars as pl


def generate_telemetry(
    n_servers: int = 3,
    n_hours: int = 24,
    seed: int = 42,
) -> pl.DataFrame:
    """Generate hourly synthetic CPU utilization."""

    if n_servers < 1 or n_hours < 1:
        raise ValueError("n_servers and n_hours must be positive")
    # Set the random seed for reproducibility
    rng = np.random.default_rng(seed)

    # Set the timestamps for the synthetic telemetry data
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    timestamps = [start + timedelta(hours=i) for i in range(n_hours)]
    # Create server-specific parameters for CPU utilization, temperature, and memory usage
    server_baselines = rng.uniform(
        low=30,
        high=70,
        size=n_servers,
    )

    server_amplitudes = rng.uniform(
        low=5,
        high=20,
        size=n_servers,
    )

    # Generate synthetic telemetry data for each server and concatenate the results
    frames = []
    for server_index in range(n_servers):
        baseline = server_baselines[server_index]
        amplitude = server_amplitudes[server_index]

        hours = np.arange(n_hours)

        daily_cycle = amplitude * np.sin(2 * np.pi * (hours - 6) / 24)

        cpu_noise = rng.normal(0, 5, n_hours)

        cpu = np.clip(
            baseline + daily_cycle + cpu_noise,
            0,
            100,
        )

        temperature = 30 + 0.5 * cpu + rng.normal(0, 2, n_hours)

        memory = np.clip(
            35 + 0.4 * cpu + rng.normal(0, 5, n_hours),
            0,
            100,
        )

        server_df = pl.DataFrame(
            {
                "timestamp": timestamps,
                "server_id": [f"srv-{server_index + 1:03d}"] * n_hours,
                "cpu_pct": cpu,
                "memory_pct": memory,
                "temperature_c": temperature,
            }
        )

        frames.append(server_df)

    return pl.concat(frames)


def inject_anomalies(
    df: pl.DataFrame,
    anomaly_fraction: float = 0.05,
    seed: int = 42,
) -> pl.DataFrame:
    """Inject labeled anomalies into synthetic telemetry."""

    if not 0 <= anomaly_fraction <= 1:
        raise ValueError("anomaly_fraction must be between 0 and 1")

    rng = np.random.default_rng(seed)

    n_rows = df.height
    n_anomalies = int(n_rows * anomaly_fraction)

    anomaly_types = np.full(
        n_rows,
        "none",
        dtype=object,
    )

    selected_indices = rng.choice(
        n_rows,
        size=n_anomalies,
        replace=False,
    )

    possible_types = [
        "cpu_spike",
        "memory_pressure",
        "overheating",
    ]

    anomaly_types[selected_indices] = rng.choice(
        possible_types,
        size=n_anomalies,
    )

    result = df.with_columns(pl.Series("anomaly_type", anomaly_types))

    result = result.with_columns((pl.col("anomaly_type") != "none").alias("is_anomaly"))

    result = result.with_columns(
        pl.when(pl.col("anomaly_type") == "cpu_spike")
        .then((pl.col("cpu_pct") + 40).clip(0, 100))
        .otherwise(pl.col("cpu_pct"))
        .alias("cpu_pct")
    )

    result = result.with_columns(
        pl.when(pl.col("anomaly_type") == "memory_pressure")
        .then((pl.col("memory_pct") + 35).clip(0, 100))
        .otherwise(pl.col("memory_pct"))
        .alias("memory_pct")
    )

    result = result.with_columns(
        pl.when(pl.col("anomaly_type") == "overheating")
        .then((pl.col("temperature_c") + 25))
        .otherwise(pl.col("temperature_c"))
        .alias("temperature_c")
    )

    return result
