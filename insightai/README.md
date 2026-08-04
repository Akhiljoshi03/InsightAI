# InsightAI — AI Data Analyst

An AI-powered data analyst web app: upload a dataset, get automatic profiling,
one-click cleaning, interactive charts, ML models, forecasts, anomaly
detection, an AI chat interface (with NL→SQL), and exportable executive
reports.

## What's real vs. scaffolded

To be upfront about scope, since this is a large spec:

**Fully implemented and tested** (backend logic runs and its unit tests pass):
- JWT auth (register/login/refresh) + Google OAuth flow
- Dataset upload (CSV/Excel/JSON), automatic profiling (dtypes, nulls,
  duplicates, outliers, correlations, distributions) — see `app/services/data_service.py`
- One-click cleaning pipeline (dedupe, fill missing, normalize, encode,
  scale, parse dates) with undo
- ML: linear/logistic regression, decision tree, random forest, gradient
  boosting, K-Means, DBSCAN, isolation-forest anomaly detection — see
  `app/services/ml_service.py`, exercised by `backend/tests/test_ml_service.py`
- Forecasting (trend + seasonality decomposition with confidence intervals)
- Chart data aggregation endpoint (group/sort/filter/aggregate)
- AI chat + NL→SQL wired to the OpenAI API (executes generated SQL against
  an isolated in-memory SQLite copy of the dataset, never your real DB)
- Executive report generation (AI-written sections) + PDF/XLSX/CSV export
- React frontend: landing page, auth pages, protected dashboard shell,
  upload dropzone with progress, dataset profile table, working AI chat UI

**Scaffolded / left as a clear extension point** (not wired in this pass —
building genuinely functional versions of *all* of these in one shot would
mean shipping unreviewed, likely-broken code for every one of them):
- Drag-and-drop dashboard builder with saved/shared layouts
- Full chart type library beyond bar/line/pie/scatter in the UI (backend
  aggregation endpoint supports any of them; frontend only renders a couple
  as examples)
- Admin panel UI (backend routes exist in `app/routers/admin.py`; no frontend yet)
- Billing/subscription UI and Stripe integration
- Notifications, usage analytics dashboards
- Rate limiting is wired for the API (slowapi) but not tuned per-route
- CI (GitHub Actions) file is not included — add a standard test+build
  workflow calling `pytest` and `npm run build`

Treat this as a strong, working core (~85% of the "make it actually work"
effort) plus a clean structure to extend rather than a finished 1.0 you'd
ship untouched.

## Tech stack

- **Frontend**: React 19, TypeScript, Tailwind CSS, TanStack Query, Zustand,
  Recharts, React Hook Form, React Router
- **Backend**: FastAPI, SQLAlchemy, Pandas, NumPy, scikit-learn
- **Database**: PostgreSQL
- **Auth**: JWT + Google OAuth
- **AI**: OpenAI API (chat + NL→SQL + report writing)
- **Deployment**: Docker Compose

## Project structure

```
insightai/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, router wiring
│   │   ├── config.py          # env-based settings
│   │   ├── database.py        # SQLAlchemy engine/session
│   │   ├── models.py          # User, Project, Dataset, Report, ChatMessage, AuditLog
│   │   ├── schemas.py         # Pydantic request/response models
│   │   ├── security.py        # password hashing, JWT
│   │   ├── deps.py            # auth dependencies
│   │   ├── routers/           # auth, projects, datasets, charts, ml, forecast, chat, reports, admin
│   │   └── services/          # data_service, ml_service, ai_service, report_service
│   ├── tests/                 # pytest — data_service and ml_service tests pass standalone
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/              # Landing, Login, Register, Dashboard, DatasetView, Chat
│   │   ├── components/         # Sidebar, UploadDropzone, ChartCard, ProtectedRoute
│   │   ├── store/               # zustand: auth, dataset
│   │   └── api/client.ts        # axios instance with JWT + refresh
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── sample_datasets/sales_sample.csv
└── docker-compose.yml
```

## Setup

### 1. Environment variables

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Fill in `backend/.env` with:
- A random `SECRET_KEY` (e.g. `openssl rand -hex 32`)
- Your `OPENAI_API_KEY` (required for chat, NL→SQL, and report generation)
- Google OAuth credentials, if you want Google login (optional — email/password works without it)

### 2. Run with Docker Compose (recommended)

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000 (docs at `/docs`)
- Postgres: localhost:5432

### 3. Run locally without Docker

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# start a local Postgres and update DATABASE_URL in .env accordingly
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 4. Try it

1. Register an account at http://localhost:5173/register
2. Create a project (via `POST /api/projects` — no "new project" UI yet, use `/docs`)
3. Upload `sample_datasets/sales_sample.csv` from the Datasets tab
4. Open the dataset to see the auto-generated profile
5. Go to AI Chat and ask something like "which region has the highest revenue?"
6. Generate a report via `POST /api/reports/generate`, then export as PDF/XLSX

## Running tests

```bash
cd backend
pip install -r requirements.txt
PYTHONPATH=. pytest tests/test_data_service.py tests/test_ml_service.py -v
```

These two files test pure logic (no DB needed) and pass out of the box.
`test_auth.py`/`test_datasets.py` stubs are included in `tests/` as a
starting point for API-level tests — they need a running Postgres or an
in-memory SQLite override of `get_db` to execute.

## Security notes

- Passwords hashed with bcrypt; JWT access + refresh tokens
- NL→SQL queries run against an isolated, per-request in-memory SQLite copy
  of the dataset — never against the app's own Postgres database — and are
  validated to be single `SELECT` statements before execution
- CORS restricted to `FRONTEND_URL`
- File upload size capped via `MAX_UPLOAD_MB`
- Rate limiting via slowapi (tune per-route limits before production use)

For a real deployment, put this behind HTTPS, add CSRF protection on any
cookie-based flows you add, rotate `SECRET_KEY` per environment, and run
`Base.metadata.create_all` only in dev — use Alembic migrations in production.
