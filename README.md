# Infrastructure Intelligence

**Predictive infrastructure monitoring and anomaly detection with Python, machine learning, and interactive analytics.**

> **Status:** In development — project scaffolding and initial dashboard are the first milestones. The features described below are planned unless marked complete.

## Overview

Infrastructure Intelligence is a portfolio project that explores how operational telemetry can be transformed into actionable insights. It will combine time-series monitoring, anomaly detection, and predictive risk modeling in an interactive Streamlit application.

The goal is to demonstrate an end-to-end data science workflow: data generation and ingestion, persistence, feature engineering, model training and evaluation, explainability, testing, and deployment.

### Planned capabilities

- **Fleet monitoring:** CPU, memory, temperature, disk I/O, and network throughput across multiple servers.
- **Interactive analytics:** Historical trends, server comparisons, metric filters, and downloadable telemetry.
- **Anomaly detection:** Unsupervised detection of unusual telemetry patterns with scored events.
- **Predictive risk:** A supervised model trained on explicitly labeled *synthetic incidents*, with a clearly defined prediction horizon.
- **Model evaluation:** Time-aware validation, baseline comparisons, error analysis, and feature importance.
- **Historical persistence:** SQL-backed telemetry, alerts, and prediction records.
- **Engineering quality:** Automated tests, linting, CI, reproducible dependencies, and a publicly accessible demo.

## Why this project?

Modern infrastructure produces high-volume, multivariate telemetry. Threshold-based alerts can miss subtle interactions and generate noisy notifications. This project investigates whether statistical and machine learning methods can provide more informative anomaly signals and forward-looking risk estimates.

**Scope and limitations:** The initial demo uses deterministic synthetic telemetry. Injected anomaly events and incident labels are not evidence of real hardware failures. Any reported predictive performance will be explicitly identified as synthetic-data performance, not production reliability.

## Technology stack

| Area | Technology |
| --- | --- |
| Application | Python 3.11, Streamlit, Plotly |
| Data | Pandas, NumPy |
| Database | SQLite, SQLAlchemy |
| Machine learning | scikit-learn (Isolation Forest and supervised baseline) |
| Development | uv, Git, VS Code |
| Quality | pytest, Ruff, GitHub Actions |
| Deployment | Streamlit Community Cloud (planned) |

## Architecture (planned)

```text
Synthetic telemetry / selected public traces
                  |
                  v
       Validation and ingestion
                  |
                  v
        SQLite / SQLAlchemy
                  |
          +-------+-------+
          |               |
          v               v
   Feature engineering  Historical queries
          |               |
          v               |
   Anomaly + risk models  |
          |               |
          +-------+-------+
                  |
                  v
        Streamlit + Plotly
      Trends / alerts / scores
```

Application logic will live in an installable `src/infrastructure_intelligence/` package, separate from the Streamlit presentation layer.

## Getting started

Prerequisites: [uv](https://docs.astral.sh/uv/) and Git.

```powershell
# From the repository root, after pyproject.toml and app.py are added:
uv sync
uv run streamlit run app.py
```

The dashboard will be available at `http://localhost:8501` once implemented. If the application has not yet been created, follow the Week 1 milestone first.

Development checks (after test and lint tooling are configured):

```powershell
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## Development roadmap

| Week | Focus | Deliverable |
| --- | --- | --- |
| 1 | Project setup, synthetic telemetry, first dashboard | Local interactive demo |
| 2 | SQL schema, ingestion, historical queries | Persistent telemetry backend |
| 3 | Feature engineering and anomaly detection | Anomaly scores and alerts |
| 4 | Supervised synthetic-incident prediction | Evaluated risk model and explanations |
| 5 | Tests, CI, documentation, UI refinement | Engineering-quality release candidate |
| 6 | Deployment and portfolio presentation | Public demo and walkthrough |

**Estimated effort:** 5–8 hours per week over 4–6 weeks, with a six-week baseline plan.

## Evaluation principles

- Use chronological train/validation/test splits to avoid future-data leakage.
- Compare learned methods against simple, interpretable baselines.
- Report precision, recall, and false-alert burden for anomaly detection.
- Define the incident prediction horizon before labeling data.
- Report classification metrics and calibration for predictive risk, where appropriate.
- Document limitations and avoid claiming synthetic results generalize to real fleets.

## Documentation

See [Project Overview](docs/project_overview.md) for scope, data contracts, architecture decisions, acceptance criteria, and milestones.

## Demo

**Coming soon.** A public Streamlit deployment link and screenshots will be added after implementation and verification.

## Data and licensing

The initial dataset will be generated synthetically within the repository. Any external datasets will be added only after checking their licenses and usage requirements. No proprietary employer data or code is used.

## License

**To be selected before public release.** Do not assume third-party datasets share the same license as this repository.
