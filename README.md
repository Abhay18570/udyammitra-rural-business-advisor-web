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
- Saved deterministic business feasibility and exact-INR financial calculations
- Smart Scheme Router with explainable financing tiers, loan caps, and contribution shortfalls

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
- `POST /api/v1/financial/analyze`
- `POST /api/v1/schemes/analyze`

Passwords use Argon2 hashing and access tokens are signed JWTs. Public registration always assigns the `USER` role.

The frontend keeps the access token in `sessionStorage` by default, or `localStorage` only when “Remember Me” is selected. Storage access is centralized in `tokenStorage.ts`; passwords and user profiles are never persisted there. This is a practical prototype choice, but production should migrate to short-lived access tokens with secure HttpOnly refresh cookies to reduce exposure to script-based attacks.

Logout clears the browser-held token. Stateless JWTs are not revoked server-side in this version.

Market Analysis now offers real OSM nearby-business evidence independently from the clearly labeled Maharashtra demonstration scoring workflow. Neither source is an exhaustive market census. Seed this data after the business catalog with `python scripts/seed_market_data.py` from `backend/`.

Modules still under development include broader external market-data integration, business-health analysis, repayment schedules, documentation and compliance assistance, RAG/AI advice, feasibility-report generation, complete RBAC, and administration APIs. Forgot-password currently provides a frontend-only notice and does not send a recovery message.

## Financial-domain assumptions

- Beneficiary margin capital is expected to represent 10% of a future project cost.
- Scheme funding may provide up to 90%, subject to the applicable scheme rules.
- A scheme-specific loan cap may reduce the loan below 90% and create an additional contribution or funding gap.
- Eligibility and terms must be verified against current official scheme guidance before application or sanction.
- Repayment, interest, EMI/installment, and moratorium calculations are not implemented yet.
- Monetary values cross API boundaries as decimal strings, are calculated with decimal arithmetic, and round half-up to paise unless a whole-rupee display is explicitly requested.

## Smart Scheme Router (Module 12)

From Financial Plan, calculate or view a saved financial analysis, then choose **Check Financing Option**. Editing margin capital clears the previous result and requires recalculation. Scheme results distinguish a business setup shortfall from a loan-cap financing shortfall.

These are **SIH prototype decision-support rules**, not guaranteed eligibility or loan approval. The canonical metadata lives in `backend/app/scheme_rules.py`; the browser renders backend results without deciding eligibility.

| Scheme | Project-cost tier | Maximum loan | Annual rate | Tenure | Moratorium |
| --- | --- | --- | --- | --- | --- |
| Micro Finance | Above ₹0, up to and including ₹1,40,000 | ₹1,25,000 | 6.50% | 36 months | 3 months |
| Term Loan | Above ₹1,40,000, up to and including ₹50,00,000 | ₹45,00,000 | 8.00% | 84 months | 6 months |

Exactly ₹14,000 margin gives a ₹1,40,000 project and ₹1,26,000 financing requirement. This stays in Micro Finance: indicative principal ₹1,25,000, shortfall ₹1,000, and total contribution ₹15,000 for the **same** project. Additional contribution is not fed back into the project-cost formula. Above ₹50 lakh, the result is `OUT_OF_SUPPORTED_RANGE` with no selected scheme, applicable principal, or scheme terms.

`POST /api/v1/schemes/analyze` requires the existing bearer token and accepts only `{"financial_analysis_id":"<owned UUID>"}`. Extra financial fields are rejected. Responses include source/rule versions, business snapshot, exact two-decimal money strings, status, scheme metadata, coverage, and deterministic reason/warning/next-step codes with parameters and English messages. Missing/foreign analyses return the same 404; incompatible versions or inconsistent saved structures return a controlled 409 requiring recalculation.

Scheme evaluation is read-only and creates no new history row. Existing financial snapshots remain unchanged; reevaluation uses the deployed scheme rule version. Repayment basis remains null and the Module 13 continuation is visibly disabled. EMI, repayment schedules, AI/RAG (Modules 16/17), reports, and scheme history are deferred.

Targeted backend checks (with the existing migrated and seeded PostgreSQL test database available):

```bash
python -m pytest tests/test_scheme_engine.py tests/test_schemes.py tests/test_financial.py tests/test_financial_engine.py tests/test_money.py tests/test_analysis_contract.py -q
```

## Real nearby business evidence (Module 14A)

Open **Market Analysis → Real Nearby Business Evidence**, select a catalog business, and choose **Find Nearby Businesses**. The existing demonstration analysis remains a separate disclosure and continues to feed the existing feasibility scores. Real OSM evidence does not change those scores.

### Setup

Apply the additive migration to your existing PostgreSQL/PostGIS database from `backend/`:

```bash
source .venv/bin/activate
alembic upgrade head
```

This adds `geocoding_cache`, `market_pois`, `nearby_query_cache`, and `provider_request_state`. It does not replace demo tables or create real-analysis history. No new packages are required. Existing PostGIS must be available (the earlier market migration already enables it).

Copy the OSM settings from `backend/.env.example` into your local configuration if you want to override defaults. The default application User-Agent contains no personal information. All provider URLs and limits are backend-only. The nearby frontend request has a 60-second timeout; other API calls retain the shared 10-second timeout. The default backend provider-work budget is 50 seconds, bounded by cancellable HTTP deadlines.

### Provider responsibilities and restrictions

Public Nominatim is used only for explicit user-triggered locality resolution, not autocomplete or POI enumeration. Review its [usage policy](https://operations.osmfoundation.org/policies/nominatim/): aggregate application traffic must stay at or below one request per second, use an identifying User-Agent, cache results, and retain attribution. Database-backed leases coordinate application workers; the default interval is 1.1 seconds and a cooldown is also applied after geocoding. Configure an alternative provider endpoint if traffic outgrows the public service.

Overpass receives only the resolved centre and backend-owned tag filters. The provider retrieves the selected 1–10 km radius plus a 100 m candidate buffer, with PostGIS enforcing the exact selected radius. Public providers can throttle or fail. Only connection-establishment failures are retried automatically, once within the remaining budget; returned HTTP failures and throttling are not repeatedly retried. No profile identity, credentials, financial data, or scheme results are sent externally.

### API and location resolution

`POST /api/v1/market/nearby` requires the existing bearer token and accepts only:

```json
{"business_slug":"tailoring-alteration","radius_km":5}
```

The backend reads the current profile's village, **taluka**, district, and state. It tries `village, taluka, district, state, India`, then `village, district, state, India`, with an India restriction. Results retain query, provider, address, precision, coordinates, fetch time, and a fingerprint of current location text. Existing profile coordinates are neither trusted automatically nor overwritten.

Ambiguous or coarse locations return `409 LOCATION_CONFIRMATION_REQUIRED`; interactive candidate confirmation is intentionally deferred. Correct the profile locality and retry. No arbitrary coordinates or location tokens are accepted in this pass. Missing location returns `409 PROFILE_LOCATION_REQUIRED`; no acceptable location returns `422 LOCATION_NOT_RESOLVED`; unknown/inactive businesses return 404; forbidden fields return 422. Provider failures return sanitized 503/504 responses and throttling returns 429 with retry guidance where available.

The response includes business/location context, selected radius configuration, selected-radius direct and related counts, nearest direct match, normalized direct and related records, source/freshness metadata, warnings, and OSM attribution. OSM IDs are strings on the wire. Matched tags are plain text, never HTML.

### Radius and matching semantics

PostGIS `geography(Point,4326)`, `ST_DWithin`, and spheroidal `ST_Distance` are authoritative. Points use longitude/latitude order. The real endpoint includes records only when unrounded `ST_Distance <= selected_km * 1000`. The indexed candidate filter has a 1 mm buffer to avoid boundary disagreement with `ST_DWithin`; the final distance predicate has no added tolerance. Kilometres are rounded only for display. Legacy fixed-band helpers remain for existing tests and compatibility.

`backend/app/osm_business_rules.py` is the versioned registry:

| Catalog slug | Direct evidence | Related evidence |
| --- | --- | --- |
| tailoring-alteration | shop=tailor; craft=tailor or dressmaker | shop=clothes |
| mobile-repair-accessories | shop=mobile_phone + mobile_phone:repair=yes; craft=electronics_repair + electronics_repair=phone | shop=mobile_phone without explicit repair |
| kirana-general-store | shop=convenience or general | shop=supermarket or grocery |
| dairy-enterprise | landuse=farmyard + produce=milk | shop=dairy; industrial=dairy |
| poultry-enterprise | landuse=farmyard + produce=eggs or poultry | shop=butcher + butcher=poultry |
| flour-mill | man_made=works + product=flour; craft=mill + product=flour | craft=mill without explicit flour evidence |
| food-processing-unit | None without a more specific product definition | industrial=food; man_made=works + product=spices or pickles |
| agri-equipment-rental | shop=agrarian + agrarian=machinery + rental=yes | shop=agrarian + agrarian=machinery without rental evidence |

Direct matches take precedence, unrelated objects are discarded, and lifecycle-tagged closed/disused/construction objects are conservatively excluded. Producer/rental mappings carry explicit weak-coverage warnings. Related objects do not contribute to direct competitor totals.

### Cache and source behavior

Geocoding successes default to 30 days; no-match/ambiguity to one hour. Complete nearby searches default to 24 hours; successful empty searches to one hour. Cache keys include provider endpoint, centre, selected radius, query version and mapping version. Exact-radius caches are used: neither smaller nor larger radius searches satisfy another radius. A few cached POIs do not prove complete search coverage: every result requires a completed query-membership record.

Refresh upserts POIs and replaces membership atomically. Failed, malformed, oversized, or partial results never overwrite a complete result. Removed members disappear from the refreshed search without deleting shared POIs. On provider failure, a matching complete query no older than seven days may be returned as **STALE CACHE**, preserving its original timestamp. Beyond that age, an error is returned. Expired geocoding is re-resolved rather than trusting an obsolete location. No automatic demo substitution occurs.

The UI distinguishes **LIVE**, **CACHE**, **STALE CACHE**, and **DEMONSTRATION**. Empty results mean: “No mapped direct competitors were found in the available OpenStreetMap data.” They never establish the absence of real competitors.

### Validation and limitations

Run mocked-provider and PostGIS tests against the existing migrated/seeded test database:

```bash
python -m pytest tests/test_geocoding.py tests/test_overpass.py tests/test_nearby_market_engine.py tests/test_nearby_market.py -q
python -m pytest -q
```

Normal tests do not call public OSM providers. One manual live check can use a profile such as Mankoli, Bhiwandi, Thane, Maharashtra and Tailoring, subject to provider availability.

The shared Google Maps visualization shows one selected-radius circle, the analysis centre, classified business markers, React-rendered info windows, source attribution, and an accessible text list. Bounds fit the selected area and returned markers when evidence geometry changes; container resizing preserves the user’s camera. Locality centres and way/relation representative centres are approximate, not premises entrances. OSM coverage and tag quality vary; duplicate physical establishments mapped as distinct elements may remain. Strict administrative/name matching may require profile correction, particularly across spelling or language variants. Cache cleanup/retention automation, interactive candidate confirmation, broader POIs, live scoring, travel times, pricing, AI/RAG and reports remain future work.

### Module 15 prerequisites (2026-09-08)

Real nearby requests require a strict integer `radius_km` from 1 through 10; missing values, booleans, strings, decimals and extra fields are rejected. The UI defaults to 5 km and clears evidence on radius/business changes without automatically searching. Responses expose `radius.selected_km`, `radius.selected_meters`, `summary.direct_competitors`, `summary.related_businesses`, and the nullable nearest direct competitor. Fixed bands are no longer part of the real API. Demo radius/scoring behavior is unchanged.

Migration `20260908_08_add_proposed_business.py` adds nullable `entrepreneur_profiles.proposed_business_id`, a foreign key to the existing catalog. Old profiles remain valid. New non-null selections must exist and be active; explicit null clears the selection. Onboarding's Capital step offers an optional catalog selection, saved with the profile. Profile displays it and editing uses the existing onboarding edit flow. Market Analysis defaults to the active saved choice on load; missing selections remain empty, and unavailable saved choices require manual selection. Manual market choices do not write the profile or modify saved analyses.

Run `alembic upgrade head` against your existing database before starting the updated backend. No Module 15 analysis engines or pages are included in these prerequisites.

Prerequisite validation: targeted backend tests passed (98); full backend suite passed (294); frontend state tests passed (5) with `node --test tests/nearbyState.test.mjs` (Node 26 used). `npm run lint`, `npm run build`, and `git diff --check` passed. Vite retains its bundle-size warning. The migration was applied to the existing isolated PostgreSQL/PostGIS test database; apply it to your application database separately. Browser interaction remains a manual check.

Manual checks: edit Profile via onboarding, choose a proposed business in Capital, save and reload Profile. Open Market Analysis and verify preselection and default 5 km. Search, then change radius/business and verify evidence clears without automatic submission. Search at 1/3/8/10 km and inspect the single circle, counts, source label and sidebar resize. Reload to restore the profile default; manual market selection must not alter Profile. Clear the saved choice and confirm Market Analysis starts empty.

## Business Intelligence & Market Feasibility (Module 15)

Business Analysis replaces the Business Health placeholder. Select a proposed business in Profile, save a matching Financial Plan, check financing, then choose **Continue to Business Analysis**. Direct sidebar access also finds the latest saved financial plan for the proposed business. Generate analysis at a selected 1–10 km radius.

`POST /api/v1/business-analysis` accepts only `{"financial_analysis_id":"<owned UUID>","radius_km":5}` and returns a saved deterministic SWOT/threat/competition/pricing-evidence response. `GET /api/v1/business-analysis/{id}` retrieves an owned immutable snapshot. Module 14A supplies real nearby evidence; no demo market ID is accepted. Apply additive migration `20260908_09_create_business_analyses.py` with `alembic upgrade head`.

Competition labels are provisional mapped-evidence classifications, never a complete market census. Inherent risks are not observed local incidents. Pricing currently returns missing-assumption guidance because the catalog has no configured unit-cost/volume/margin model; local prices and purchasing-power adjustments are unavailable. Profile capital differences are shown explicitly without overwriting financial snapshots. No LLM, RAG, reports, history UI or repayment features are added.

See [Module 15 implementation and validation report](MODULE15_IMPLEMENTATION.md) for exact files, formulas, source/evidence design, API/persistence details, test results, limitations and browser checks.


## Google Maps visualization

The frontend uses Google Maps JavaScript API through `@vis.gl/react-google-maps` for visualization. Add `VITE_GOOGLE_MAPS_API_KEY` to your existing local frontend `.env` and restart Vite. Enable Maps JavaScript API for that key’s project. Never commit the key; `.env.example` contains only an empty placeholder. The browser key is necessarily visible to browsers: configure website/referrer and API restrictions in your Google Cloud project.

Competitor/business evidence comes through FastAPI from OpenStreetMap/Overpass by default, or the optional explicitly configured Google Places provider. Exact selected-radius filtering and distance calculations remain PostGIS-based. Google Places Nearby Search is an optional backend provider; Google Geocoding and browser-side competitor discovery are not implemented. Saved Business Analysis maps render their existing evidence snapshots.

Missing configuration, script loading failure, authentication failure, and a 20-second loading timeout produce a message inside the map area; statistics and text evidence remain usable. Blue **C** identifies the analysis centre, red **D** direct competitors, and amber **R** related businesses. The demonstration map retains separate demo categories. Advanced markers currently use Google’s `DEMO_MAP_ID`; a project-owned map ID can replace it for production configuration.

Run `node --test tests/*.test.mjs` (Node 26), `npm run lint`, `npm run build`, and `git diff --check`. Tests mock the map integration and make no live Google API requests. See [the migration verification checklist](GOOGLE_MAPS_MIGRATION.md) for browser checks and limitations.

## Optional Google Places evidence provider

Overpass remains the default (`NEARBY_MARKET_PROVIDER=overpass`). The backend can explicitly select `google` using its separate `GOOGLE_PLACES_API_KEY`; frontend map configuration stays unchanged. Apply migration `20260908_10` before using the provider-capable backend. See [Google Places provider configuration, mappings, storage limitations, and manual checks](GOOGLE_PLACES_PROVIDER.md). Google returns a ranked subset, not an establishment census. PostGIS remains authoritative for distances and exact radius inclusion. No automatic cross-provider fallback is performed.
