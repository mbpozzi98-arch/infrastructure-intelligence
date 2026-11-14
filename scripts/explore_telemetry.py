import plotly.express as px

from infrastructure_intelligence.data.synthetic import (
    generate_cpu_telemetry,
)

# Generate one week of telemetry
df = generate_cpu_telemetry(n_hours=168)

# Convert wide-format data into long-format data
long_df = df.melt(
    id_vars=["timestamp", "server_id"],
    value_vars=[
        "cpu_pct",
        "memory_pct",
        "temperature_c",
    ],
    var_name="metric",
    value_name="value",
)

fig = px.line(
    long_df,
    x="timestamp",
    y="value",
    color="metric",
    title="Synthetic Server Telemetry — 7 Days",
    labels={
        "timestamp": "Timestamp (UTC)",
        "value": "Measurement",
        "metric": "Telemetry Metric",
    },
)

fig.update_layout(
    hovermode="x unified",
    height=550,
)

fig.show()

metrics = [
    "cpu_pct",
    "memory_pct",
    "temperature_c",
]

correlation_matrix = df[metrics].corr()

print("\\nCorrelation Matrix:")
print(correlation_matrix.round(3))
