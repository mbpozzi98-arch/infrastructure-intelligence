import numpy as np
import pandas as pd


def generate_cpu_telemetry(
    n_hours: int = 24,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate hourly synthetic CPU utilization."""

    # Set the random seed for reproducibility
    rng = np.random.default_rng(seed)

    # Set the timestamps for the synthetic telemetry data
    timestamps = pd.date_range(
        start="2026-01-01",
        periods=n_hours,
        freq="h",
        tz="UTC",
    )

    # Set the baseline CPU utilization and generate random noise and a periodic daily cycle
    hours = np.arange(n_hours)

    amplitude = 15.0

    daily_cycle = amplitude * np.sin(2 * np.pi * (hours - 6) / 24)

    baseline = 50.0

    noise = rng.normal(
        loc=0,
        scale=5,
        size=n_hours,
    )

    cpu = np.clip(
        baseline + daily_cycle + noise,
        0,
        100,
    )

    temperature_noise = rng.normal(
        loc=0,
        scale=2,
        size=n_hours,
    )

    temperature = 30 + 0.5 * cpu + temperature_noise

    memory_noise = rng.normal(
        loc=0,
        scale=5,
        size=n_hours,
    )

    memory = np.clip(
        35 + 0.4 * cpu + memory_noise,
        0,
        100,
    )
    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "server_id": "srv-001",
            "cpu_pct": cpu,
            "temperature_c": temperature,
            "memory_pct": memory,
        }
    )
