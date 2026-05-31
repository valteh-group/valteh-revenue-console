# Valteh Economics Dashboard

Internal economics, pricing, and business management dashboard for Valteh service lines:

- SAREMI document validation
- Graphos graph analytics
- Blockchain / BaaS property registry services
- SIGEN / Notarial Platform

The app tracks fixed costs, variable costs, usage, revenue, margins, pricing scenarios, and client-level profitability.

## Tech Stack

- Python 3.11+
- Dash
- Dash Bootstrap Components
- Plotly
- Pandas
- SQLAlchemy
- Pydantic
- SQLite locally, PostgreSQL-ready through `DATABASE_URL`
- Pytest
- Ruff and Black
- Docker and Docker Compose

## Install

```bash
cd Valteh_Revenue_App
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
copy .env.example .env
```

On macOS/Linux, activate with:

```bash
source .venv/bin/activate
```

## Run Locally

```bash
python -m app.main
```

or:

```bash
python app/main.py
```

Then open:

```text
http://localhost:8050
```

## Run Tests

```bash
pytest
```

## Format and Lint

```bash
black .
ruff check .
```

## Run With Docker

```bash
copy .env.example .env
docker compose up --build
```

## Deploy

For Render or similar hosts, use the repository root as the project directory.

```text
Build command: pip install -e .
Start command: gunicorn app.main:server
```

The app also supports `python -m app.main` and reads the host-provided `PORT` environment variable.

## Seed Data

The app reads the current pilot seed data from four CSV files:

- `data/seed_clients.csv`
- `data/seed_costs.csv`
- `data/seed_usage.csv`
- `data/seed_pricing_plans.csv`

Pilot assumptions are based on:

- Queretaro RPP request data from `solicitudes_RPP.xlsx`, which shows roughly 25.5k monthly state-level requests in the 2023 extract.
- Notary document-validation logic of roughly 2 people per registry matter and 6-8 documents per person.
- Current SAREMI pilot infrastructure cost: Hetzner CX41 at about $370 MXN/month plus Claude document analysis at about $0.95 MXN/document.
- Future-state blockchain/BaaS cost ranges from `modelo economico.pdf`, included as inactive benchmark cost rows because the current pilot is focused on SAREMI, some Graphos visualization, and lightweight blockchain audit anchoring.

The repository layer in `app/data/repositories.py` exposes this data to the UI and domain logic. `app/data/database.py` and `app/data/schemas.py` define the SQLAlchemy foundation for moving from CSV-backed local data to SQLite or PostgreSQL persistence.

## Project Structure

```text
app/
  main.py                 Dash app factory and local entry point
  config.py               Environment-based settings
  layout.py               Global shell and sidebar navigation
  routes.py               Page routing
  pages/                  Dash page layouts
  components/             Reusable KPI, chart, table, filter, and form components
  domain/                 Pure business logic and domain models
  data/                   Database setup, ORM schemas, repositories, seed helpers
  integrations/           Placeholder API clients for future systems
  utils/                  Formatting, dates, and validation helpers
tests/                    Unit tests for pricing, costs, and unit economics
data/                     CSV seed data
migrations/               Reserved for Alembic migrations
```

## Add a New Service Line

1. Add the service definition in `SeedRepository.services()` or the future `services` table.
2. Add usage event types to `data/seed_usage.csv`.
3. Add matching variable cost rates to `data/seed_costs.csv`.
4. Add pricing fields or event mapping in `app/domain/revenue_engine.py` if the service has billable units.
5. Add charts or tables in the relevant page module if the service needs custom display.

## Connect Future APIs

Integration placeholders live in `app/integrations/`:

- `fetch_saremi_usage()`
- `fetch_llm_token_usage()`
- `fetch_graphos_usage()`
- `fetch_blockchain_usage()`
- `fetch_platform_clients()`

Replace the mock return values with REST client code, normalize the payloads into domain models, and persist them through a SQL repository. Keep API authentication and endpoints in `.env`, not in source code.

## Production Notes

Set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL, for example:

```text
postgresql+psycopg2://user:password@host:5432/valteh_economics
```

Keep business calculations in `app/domain/`. Dash callbacks and page modules should call domain functions and repositories rather than embedding pricing, cost, or margin logic directly in the UI.
