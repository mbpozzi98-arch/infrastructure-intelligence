import numpy as np
import pandas as pd


def generate_telemetry(
    n_servers: int = 3,
    n_hours: int = 24,
    seed: int = 42,
) -> pd.DataFrame:
    """Generate hourly synthetic CPU utilization."""

    if n_servers < 1 or n_hours < 1:
        raise ValueError("n_servers and n_hours must be positive")
    # Set the random seed for reproducibility
    rng = np.random.default_rng(seed)

    # Set the timestamps for the synthetic telemetry data
    timestamps = pd.date_range(
        start="2026-01-01",
        periods=n_hours,
        freq="h",
        tz="UTC",
    )

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

        server_df = pd.DataFrame(
            {
                "timestamp": timestamps,
                "server_id": f"srv-{server_index + 1:03d}",
                "cpu_pct": cpu,
                "memory_pct": memory,
                "temperature_c": temperature,
            }
        )

        frames.append(server_df)

    return pd.concat(frames, ignore_index=True)
