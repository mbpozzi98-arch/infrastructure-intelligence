from infrastructure_intelligence.data.synthetic import (
    generate_telemetry,
)

df = generate_telemetry(
    n_servers=3,
    n_hours=168,
    seed=42,
)

print(df.groupby("server_id")["cpu_pct"].agg(["mean", "std", "min", "max"]))

import plotly.express as px

fig = px.line(
    df,
    x="timestamp",
    y="cpu_pct",
    color="server_id",
    title="Fleet CPU Utilization",
)

fig.update_yaxes(range=[0, 100])
fig.show()
