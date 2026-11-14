# Project Overview — Infrastructure Intelligence

## 1. Executive summary

Infrastructure Intelligence is a six-week, portfolio-oriented engineering and data science project. It demonstrates a reproducible path from multivariate server telemetry to monitoring dashboards, anomaly detection, and predictive incident-risk analytics. The intended audience includes data science, machine learning engineering, and software engineering hiring teams.

**Primary outcome:** a working public Streamlit demo backed by documented data pipelines, SQL persistence, trained and evaluated models, automated tests, and CI.

**Time budget:** 5–8 hours per week (approximately 30–48 hours total).

## 2. Problem statement

Operators monitor CPU, memory, temperature, disk, and network measurements to identify unhealthy infrastructure. Static thresholds are useful but may generate excessive alerts and overlook multivariate deviations. This project explores two separate questions:

1. **Anomaly detection:** Is a telemetry observation or short time window unusual relative to learned normal patterns?
2. **Predictive incident risk:** Given telemetry available at time *t*, how likely is a defined incident within a future prediction horizon?

An anomaly score is not automatically a calibrated failure probability. The product must keep those concepts separate.

## 3. Target users and core workflows

**Target user:** an infrastructure analyst or operations engineer investigating a fleet of simulated servers.

**Core workflows:**

1. Inspect fleet-level health metrics and historical trends.
2. Select a server and compare telemetry dimensions.
3. Investigate detected anomalies and their contributing features.
4. Review predicted incident risk, the prediction horizon, and model limitations.
5. Export a filtered dataset or review historical model results.

## 4. MVP scope

### In scope

- Deterministic synthetic telemetry for a small fleet, with configurable server count and duration.
- Hourly timestamped CPU, memory, temperature, network, and disk-I/O metrics.
- Controlled injected anomalous patterns, with event indicators retained separately from model inputs.
- SQLite database accessed through SQLAlchemy.
- Streamlit/Plotly dashboard with filters, fleet metrics, trends, and alert history.
- Isolation Forest anomaly detection and an interpretable baseline comparison.
- Supervised prediction for explicitly defined *synthetic incident labels* and a fixed forecast horizon.
- Time-based evaluation, feature importance, unit tests, CI, and a public demo.

### Out of scope for MVP

- Real-time production telemetry collection or operational incident response.
- Distributed streaming, Kubernetes, cloud infrastructure provisioning, authentication, or multi-tenancy.
- Claims of validated hardware-failure prediction on real infrastructure.
- An independent API service unless time remains after the end-to-end application works.

## 5. Data strategy and contracts

### Initial source

Use a seeded synthetic generator to ensure deterministic tests and a consistent demo. Later, assess publicly available workload traces or storage-device failure datasets as distinct validation or extension tasks, subject to licensing and schema compatibility.

### Proposed telemetry schema

| Field | Type | Meaning |
| --- | --- | --- |
| timestamp | UTC datetime | Observation time |
| server_id | string | Stable server identifier |
| cpu_pct | float | CPU utilization, 0–100 |
| memory_pct | float | Memory utilization, 0–100 |
| temperature_c | float | Simulated device temperature in Celsius |
| network_mbps | float | Simulated network throughput |
| disk_io_mbps | float | Simulated disk throughput |
| injected_anomaly | boolean | Synthetic injected-event indicator; not a model input |

**Primary key / uniqueness:** `(server_id, timestamp)` for telemetry observations.

**Data validation:** non-null keys, UTC timestamps, bounded percentages, nonnegative throughput, uniqueness, stable units, and explicit missing-value handling.

### Modeling labels

- `injected_anomaly`: indicator of a deliberately injected unusual telemetry event, useful for controlled evaluation but not equivalent to a hardware failure.
- `synthetic_incident`: separately generated outcome using a documented incident simulation mechanism.
- `incident_within_horizon`: label defined from future incident occurrence within a predetermined horizon, such as 24 hours; exclude any future-derived fields from features.

Do not use an incident-generation rule that is simply a copy of the model's input threshold and then present the result as independent evidence of prediction quality. Document the simulation's assumptions and the risk of overly optimistic performance.

## 6. Architecture

```text
[Deterministic synthetic generator]
               |
               v
     [Validation + ingestion]
               |
               v
     [SQLite via SQLAlchemy] <------ [Historical predictions]
               |
        +------+------+
        |             |
        v             v
 [Historical query] [Feature pipeline]
        |             |
        |       +-----+-----+
        |       |           |
        |       v           v
        |   [Isolation] [Supervised]
        |   [Forest]    [risk model]
        |       |           |
        +-------+-----------+
                |
                v
       [Monitoring services]
                |
                v
       [Streamlit + Plotly]
```

### Module responsibilities

- `data/`: synthetic generation, validation, ingestion.
- `database/`: ORM models, transactions, and query functions.
- `features/`: leakage-aware rolling features and transformations.
- `ml/`: training, inference, evaluation, and artifact versioning.
- `services/`: orchestration of database queries and model outputs.
- `app.py`: presentation and user interaction only.
- `tests/`: deterministic unit and integration tests.

The app should never silently retrain a model on every page refresh. Training should be a deliberate, reproducible script or pipeline.

## 7. Machine learning plan

### Anomaly detection

- Start with rule-based thresholds as a baseline.
- Fit Isolation Forest using selected telemetry features and, if useful, rolling statistics.
- Split data chronologically; do not learn preprocessing statistics from future periods.
- Evaluate event detection, precision/recall against injected anomalies, and false-alert burden.
- Distinguish point-level from event-level metrics and discuss contamination assumptions.

### Incident prediction

- Specify a prediction horizon and labeling logic before training.
- Start with logistic regression or a simple tree-based baseline, then compare a gradient-boosted model if time permits.
- Use chronological splits and consider a gap/embargo where overlapping windows create leakage risk.
- Report PR-AUC, precision/recall at an operating threshold, confusion matrix, and calibration where appropriate.
- Explain features using permutation importance; SHAP is optional.
- Call scores **synthetic incident risk**, not real-world failure probabilities.

## 8. Persistence design

Proposed tables:

- `servers`: server metadata and identifiers.
- `telemetry`: unique timestamped measurements by server.
- `anomaly_scores`: score, detector version, and observation reference.
- `predictions`: incident-risk score, horizon, model version, and inference time.
- `model_runs`: training metadata, feature list, split boundaries, parameters, and metrics.

Use SQLAlchemy sessions and explicit transactions. For public deployment, seed a small read-only demo dataset if persistent writes are unavailable on the hosting platform.

## 9. Quality and deployment

- **Dependencies:** uv-managed `pyproject.toml` and committed `uv.lock`.
- **Tests:** generator reproducibility, schema checks, ingestion idempotence, query correctness, feature leakage checks, and inference schema validation.
- **Static checks:** Ruff lint and formatting.
- **CI:** GitHub Actions on push and pull request.
- **Deployment:** Streamlit Community Cloud with a documented dependency export if required.
- **Documentation:** README, this overview, screenshots, model card, and limitations.

## 10. Weekly milestones and acceptance criteria

| Week | Deliverable | Acceptance criteria |
| --- | --- | --- |
| 1 | Local dashboard | uv environment reproducible; synthetic telemetry plotted; server/metric filters work; tests pass |
| 2 | SQL backend | telemetry persists; re-ingestion does not duplicate rows; historical queries drive charts |
| 3 | Anomaly detection | saved model scores data; alerts displayed; baseline and evaluation documented |
| 4 | Incident prediction | horizon defined; time-aware validation; metrics and feature explanations shown |
| 5 | Quality and polish | CI green; tests cover critical paths; docs and UI reviewed |
| 6 | Public release | deployed demo works; README links to demo; screenshots and limitations included |

## 11. Success definition

The project is complete when a reviewer can clone the repository, reproduce the environment with uv, run tests, launch the dashboard, inspect historical telemetry and model outputs, and understand what was measured versus simulated. The public demo should be usable without credentials or access to private data.

## 12. Risks and tradeoffs

- **Synthetic-data realism:** results may be easier than real operations; document this prominently.
- **Label leakage:** future incident information must not enter model features.
- **Time constraints:** prioritize a working vertical slice over distributed-system complexity.
- **Deployment persistence:** hosted filesystem behavior may require bundled seeded data rather than runtime database writes.
- **Dataset licensing:** verify licenses before redistribution or public use.

## 13. Immediate next steps

1. Initialize or adapt the existing repository with uv without overwriting current files.
2. Add the Week 1 synthetic telemetry generator and tests.
3. Build a Streamlit dashboard for fleet KPIs, server selection, time-series trends, and CSV export.
4. Commit the first working milestone and verify tests locally.
