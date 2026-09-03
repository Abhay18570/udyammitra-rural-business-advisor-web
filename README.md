# UdyamMitra

UdyamMitra is an AI-assisted rural entrepreneurship decision-support platform. This repository contains the React frontend and the FastAPI backend foundation.

## Prerequisites

- Node.js and npm
- Python 3.9 or newer
- PostgreSQL for database-backed modules (not required for the current root and health endpoints)

## Frontend setup

```bash
npm install
cp .env.example .env
npm run dev
```

The frontend is available at [http://localhost:5173](http://localhost:5173).

Useful checks:

```bash
npm run lint
npx tsc -b
npm run build
```

## Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The backend exposes:

- API root: [http://localhost:8000](http://localhost:8000)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- OpenAPI schema: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
- Health check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- Optional database check: [http://localhost:8000/api/v1/health/database](http://localhost:8000/api/v1/health/database)

Run backend tests from `backend/` with:

```bash
source .venv/bin/activate
pytest
```

## Database and migrations

Start and inspect the local Homebrew PostgreSQL service with:

```bash
brew services start postgresql@18
brew services list | grep postgresql@18
/opt/homebrew/opt/postgresql@18/bin/pg_isready
```

Open an application-role PostgreSQL session (the password remains in the ignored `backend/.env` file and is not documented here):

```bash
/opt/homebrew/opt/postgresql@18/bin/psql -h localhost -U udyammitra_app -d udyammitra -W
```

Set `DATABASE_URL` in `backend/.env` to a PostgreSQL SQLAlchemy URL using the psycopg driver, for example:

```dotenv
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/udyammitra
```

Alembic reads `Base.metadata` from `app.db.base`. Migrations currently create users, entrepreneur profiles, existing-business details, and the business knowledge catalog. Future deployments are intended to enable these PostgreSQL extensions before dependent migrations are introduced:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;
```

Neither extension is required for the current application health endpoint.

Create a future migration from the `backend/` directory with:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Current scope

The application currently implements:

- Public landing and authentication pages
- JWT registration, login, session restoration, logout, and protected role-aware routes
- Six-step entrepreneur onboarding with resumable PostgreSQL persistence
- Entrepreneur profile viewing and editing
- A personalized dashboard based on saved profile data
- A searchable and filterable business catalog with detailed business pages

Available domain endpoints include:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/profile`
- `PUT /api/v1/profile`
- `GET /api/v1/businesses`
- `GET /api/v1/businesses/{id_or_slug}`
- `GET /api/v1/market/locations`
- `POST /api/v1/market/analysis`
- `GET /api/v1/market/analyses/latest`
- `GET /api/v1/market/analyses/{analysis_id}`

Passwords use Argon2 hashing and access tokens are signed JWTs. Public registration always assigns the `USER` role.

The frontend keeps the access token in `sessionStorage` by default, or `localStorage` only when “Remember Me” is selected. Storage access is centralized in `tokenStorage.ts`; passwords and user profiles are never persisted there. This is a practical prototype choice, but production should migrate to short-lived access tokens with secure HttpOnly refresh cookies to reduce exposure to script-based attacks.

Logout clears the browser-held token. Stateless JWTs are not revoked server-side in this version.

Hyper-local market analysis and competitor mapping currently use clearly labelled, curated Maharashtra demonstration data rather than a live or exhaustive market census. Seed this data after the business catalog with `python scripts/seed_market_data.py` from `backend/`.

Modules still under development include authoritative external market-data integration, personalized opportunity scoring, business-health analysis, financial planning, scheme routing, repayment schedules, documentation and compliance assistance, RAG/AI advice, feasibility-report generation, complete RBAC, and administration APIs. Forgot-password currently provides a frontend-only notice and does not send a recovery message.

## Financial-domain assumptions

- Beneficiary margin capital is expected to represent 10% of a future project cost.
- Scheme funding may provide up to 90%, subject to the applicable scheme rules.
- A scheme-specific loan cap may reduce the loan below 90% and create an additional contribution or funding gap.
- Eligibility and terms must be verified against current official scheme guidance before application or sanction.
- Repayment, interest, EMI/installment, and moratorium calculations are not implemented yet.
- Monetary values cross API boundaries as decimal strings, are calculated with decimal arithmetic, and round half-up to paise unless a whole-rupee display is explicitly requested.
