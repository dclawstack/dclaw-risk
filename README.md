# DClaw Risk

> Enterprise risk management with AI insights. Identify, assess (qualitative + FAIR Monte Carlo), and mitigate risks with a domain-aware Copilot.

**Status:** P0 foundation complete (per `REVISED-PRD.md` v2.3).

## P0 features

| # | Feature | Backend | Frontend |
|---|---------|---------|----------|
| P0.1 | **AI Risk Copilot** | `/api/v1/ai/{risk-chat,identify-risks,classify-risk}` | Floating chat (`risk-copilot.tsx`) on every page |
| P0.2 | **Risk Register** | `/api/v1/risks` (full CRUD, filter, AI-classify) | `/risks` table + create modal + heat map |
| P0.3 | **Risk Assessment** | `/api/v1/risks/{id}/assessments/{qualitative,quantitative}` | `/risks/[id]` with qualitative form + FAIR Monte Carlo + loss-exceedance curve |
| P0.4 | **Control Mapping** | `/api/v1/controls`, `/api/v1/risks/{id}/controls` | `/controls` catalogue + risk-detail map/unmap |

## Quick start

```bash
cp .env.example .env

# Bring up Postgres + backend + frontend
docker compose up --build

# → frontend: http://localhost:3092
# → backend:  http://localhost:18162/docs
```

For local dev without Docker:

```bash
# Backend
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/alembic upgrade head
.venv/bin/uvicorn app.api.main:app --reload --port 18162

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## Architecture

- **Frontend** — Next.js 14 (App Router) + Tailwind + shadcn/ui (pre-built components in `frontend/src/components/ui/`)
- **Backend** — FastAPI + Pydantic v2 + SQLAlchemy 2.0 (async, with `Mapped`/`mapped_column`)
- **Database** — Postgres 16, Alembic migrations
- **AI** — Provider abstraction with Ollama (local) default and OpenRouter fallback. See `backend/app/services/llm.py`.
- **Auth** — Logto JWT validation with `DEV_AUTH_BYPASS=true` escape hatch for development.

## Tests

```bash
cd backend
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_risk_test \
  .venv/bin/python -m pytest -v
```

Pure-math tests (`tests/test_fair.py`, `tests/test_llm.py`) run without a database. API tests skip if Postgres is unavailable.

## Configuration

All settings come from environment variables (see `.env.example`):

| Variable | Default | Notes |
|----------|---------|-------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_risk` | |
| `CORS_ORIGINS` | `["http://localhost:3092"]` | JSON array |
| `OLLAMA_URL` | `http://localhost:11434` | Default LLM provider |
| `OLLAMA_MODEL` | `llama3.1` | |
| `OPENROUTER_API_KEY` | _(unset)_ | If set, used as fallback |
| `OPENROUTER_MODEL` | `meta-llama/llama-3.1-8b-instruct` | |
| `LOGTO_ISSUER`, `LOGTO_JWKS_URI`, `LOGTO_AUDIENCE` | _(unset)_ | Production auth |
| `DEV_AUTH_BYPASS` | `true` | Set to `false` in production |

## Roadmap

P1 features (Incident Linkage, KRIs, Risk Reporting, Compliance integration) and P2 (Emerging Risk, Risk Culture, Third-Party, Scenario Planning) are tracked in `REVISED-PRD.md` and `PLAN-v1.2.md`.

## Conventions

Inherited from `dclaw-scaffold`:
- `pytest-asyncio==0.24.0` pinned in `requirements.txt` (newer versions break fixture scoping).
- Pre-built UI components live in `frontend/src/components/ui/`. Do **not** run the shadcn CLI v4 or install `@base-ui/react` — both break the Tailwind v3 build.
- All SQLAlchemy models inherit from `app.models.base.Base`.
