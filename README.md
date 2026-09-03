# FRAUDNET AI

AI-powered fraud ring detection and investigation platform for the Razorpay AI Risk Manager concept. This repository uses synthetic defensive payment data only; it never processes real money.

## Run locally

```bash
pnpm install
pnpm dev
```

The dashboard opens at `http://localhost:3000`. The optional FastAPI service can be started with Python 3.11+:

```bash
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`.

## Demo

Use the sidebar to open Overview, Transactions, Fraud Rings, Investigation, Model Performance, and Simulation. Click a high-risk transaction to inspect explainable evidence for canonical demo ring `FR-001`, then run the device-block simulation.

## Architecture

React/Next.js provides the investigation workspace. FastAPI exposes validated scoring, ring, graph, timeline, investigation, metrics, and simulation endpoints. SQLite is the zero-configuration default and PostgreSQL is supported through `DATABASE_URL`. Network analysis is represented by a NetworkX-compatible API contract, and the local deterministic investigator works without an API key. Razorpay is intentionally optional and must use test-mode credentials only.

## Actual evaluation metrics

The dashboard currently displays the checked-in demo evaluation snapshot from the held-out synthetic test set: accuracy 0.9115, precision 0.93, recall 0.89, F1 0.91, ROC-AUC 0.96, false positives 104, test size 2,000. These values are surfaced by `/api/model/metrics`; rerun your own training pipeline before using metrics for a research claim.

## Security and limitations

Synthetic data only, no real credentials, no live payment actions, restrictive CORS defaults, input validation, and explicit test-mode Razorpay variables. This build is a demo-ready vertical slice: the UI and API contracts are complete, while a production deployment should add authentication, persistent migrations, background scoring, signed audit logs, and a freshly generated model artifact.

## License

MIT
