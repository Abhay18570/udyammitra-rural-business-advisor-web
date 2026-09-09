# Module 15 — completion report

## Audit and continuation

The continuation inspected `git status`, `git diff --stat`, `git diff`, and the Module 15 files already created. Earlier profile/radius, scheme, financial and sidebar changes were preserved. No prerequisite was reimplemented.

Already present: shared typed context/response schemas, profile interpretation, competition/threat/SWOT/pricing engines, orchestration service, owner-scoped repository/API registration, snapshot model and additive migration, initial Business Analysis page and navigation. No Module 15 tests existed yet. The scheme continuation import existed but its link was unfinished. Migration execution and validation remained incomplete.

Completed in this continuation: the scheme CTA, saved-result navigation isolation, typed JSON evidence with value-type metadata, profile observation timestamps, stable catalog risk identifiers and categories, tailoring skill-dependency finding, missing-assumption presentation, 66 Module 15 tests, existing-database migration, isolated integration validation, full regression/build checks, and documentation. No LLM, RAG, report/PDF/history UI, repayment or deployment work was added.

## Exact files

Created for Module 15, including files begun before continuation:

```text
backend/app/business_analysis_rules.py
backend/app/schemas/business_analysis.py
backend/app/engines/profile_evidence.py
backend/app/engines/competitor_analysis_engine.py
backend/app/engines/threat_engine.py
backend/app/engines/swot_engine.py
backend/app/engines/pricing_engine.py
backend/app/models/business_analysis.py
backend/app/repositories/business_analysis_repository.py
backend/app/services/business_analysis_service.py
backend/app/api/v1/endpoints/business_analysis.py
backend/alembic/versions/20260908_09_create_business_analyses.py
backend/tests/test_business_analysis_engines.py
backend/tests/test_business_analysis.py
src/types/businessAnalysis.ts
src/services/businessAnalysisService.ts
src/features/businessAnalysis/BusinessAnalysisPage.tsx
MODULE15_IMPLEMENTATION.md
```

Existing files modified for Module 15:

```text
backend/app/api/v1/router.py
backend/app/models/__init__.py
src/routes/AppRouter.tsx
src/config/navigation.ts
src/features/financial/SchemeEligibilityPanel.tsx
src/index.css
README.md
```

Other working-tree changes belong to earlier work and were retained.

## Context and evidence

`BusinessAnalysisContext` contains typed entrepreneur, catalog business, financial snapshot, scheme evaluation, budget, real-market response (including resolved location/provenance), pricing assumptions, evidence registry, profile fingerprint, quality and rule versions.

`BusinessAnalysisService` validates owned sources, captures a source fingerprint, calls the existing `NearbyMarketService`, reloads and revalidates sources after provider I/O, then runs competition → threats → pricing → SWOT and saves an immutable snapshot. Engines contain no ORM, network or persistence operations.

Business comes from the owned financial snapshot and must match the persisted profile proposed-business ID. Missing/mismatched choices require correction. Current profile own capital differing from saved margin is explicitly reported as a budget inconsistency and weakness; it does not silently replace the saved financial scenario. Missing own capital remains `NOT_RECORDED`. Catalog cost changes require financial recalculation; current qualitative knowledge is hashed and captured separately. Existing-business metrics are included only for an exact normalized catalog name/slug match in the declared category, never a broad category such as Retail.

Evidence IDs include `profile.skills`, `profile.resources`, `profile.budget`, `catalog.risks`, `catalog.requirements`, `financial.setup`, `financial.scheme`, `market.direct`, `market.related`, `market.quality`, `pricing.assumptions`, and `data.demographics`. Values are JSON-typed and expose `value_type`; records include source kind/reference, units, timestamps, geography/radius where applicable, self-report/assumption flags and limitations. Findings link to evidence IDs; SWOT threats also link to existing threat finding IDs.

Profile interpretation distinguishes `CONFIRMED_SELF_REPORTED` (exact normalized match), `TENTATIVE_ALIAS_MATCH` (legacy broad alias), and `NOT_RECORDED`. Machinery cannot confirm electrical infrastructure and Land cannot confirm a cattle shed. Old feasibility aliases and scoring behavior are unchanged.

Versions: `business-analysis-v1`, `swot-v1`, `threat-v1`, `mapped-competition-v1`, `pricing-v1`, `profile-evidence-v1`, plus actual financial, scheme and OSM mapping versions. Catalog and full context hashes support reproducibility. Ordering is deterministic for an identical context and versions.

## Findings

SWOT strengths cover explicitly declared requirements and project capacity within catalog setup estimates. Weaknesses cover tentative/unrecorded requirements, positive setup gap, positive scheme-cap gap and differing budget declarations. Fresh related mapped businesses support a possible referral/channel investigation opportunity. Threat-quadrant items reference the shared threat findings. Zero mapped competitors never generates a low-real-competition strength or unmet-demand claim; quadrants may be empty. Setup gaps and scheme gaps remain separate comparisons.

Catalog risk text remains authoritative; Module 15 adds stable identifiers, risk categories, evidence distinctions and mitigation guidance:

| Business | Catalog-backed risk coverage | Mitigation emphasis |
| --- | --- | --- |
| Tailoring | Seasonal orders, machine breakdown, delayed payments, stitching/measurement dependency | Scheduling, maintenance, skills and agreed delivery/payment terms |
| Mobile repair | Device changes, parts quality, customer data exposure, warranty liability | Training, suppliers, consent/data protection and repair records |
| Kirana | Expiry, customer credit, price volatility, theft/damage | Stock rotation, credit limits, price records and secure inventory |
| Dairy | Animal illness, feed costs, spoilage, water scarcity | Veterinary, feed/water and hygienic collection/cooling plans |
| Poultry | Disease, feed volatility, mortality, output-price fluctuations | Biosecurity, flock records and buyer/feed planning |
| Flour mill | Injury, dust, power interruption, contamination, maintenance dependency | Guards, operator training, electrical checks, cleaning and maintenance |
| Food processing | Contamination, inconsistent quality, raw-material changes, unsold short-life inventory | Batch/recipe records, sourcing, shelf-life and hygiene controls |
| Equipment rental | Damage, seasonal under-utilization, delayed payments, operator injury | Booking/condition records, maintenance, operator checks and payment terms |

Threat evidence kinds are `OBSERVED_LOCAL`, `SELF_REPORTED`, `INHERENT_BUSINESS_MODEL`, and `DATA_LIMITATION`. Inherent risks have unclassified severity and null likelihood. Missing explicit requirements receive medium confirmation priority; positive funding gaps receive high priority with the exact reason. Fresh mapped-pressure findings use the provisional rule's severity. No local disease, supplier shortage, electricity failure, or probability is invented.

## Competition

For selected radius R km and N direct records, area = πR² and mapped density = N/(πR²), labeled “Mapped direct competitors per km².” Related records never contribute to N. Nearest and average distances use unrounded PostGIS distances; average is returned in metres. Zero complete-query results have density zero and null nearest/average. Incomplete coverage produces unavailable metrics rather than a false zero.

Distance concentration bands are 0–1, >1–3, >3–5 and >5–R km, clipped to R with zero-width bands omitted. They are not geographic clusters.

Provisional thresholds:

- `HIGH_MAPPED_PRESSURE`: density ≥ 3/π AND nearest ≤ 0.5 km.
- `MODERATE_MAPPED_PRESSURE`: otherwise density ≥ 1/π OR nearest ≤ 1 km.
- `LOW_MAPPED_PRESSURE`: otherwise at least one direct mapped record.
- `NO_MAPPED_DIRECT_EVIDENCE`: complete coverage and zero direct records, subject to quality gates.
- `UNCLASSIFIED_LIMITED_MAPPING`: weak/unsupported mapping.
- `STALE_EVIDENCE`: historical metrics retained; current label withheld.
- `UNAVAILABLE_INCOMPLETE_COVERAGE`: incomplete provider coverage; service refuses to persist a completed analysis.

Quality-gate priority is incomplete → stale → limited mapping → zero → provisional thresholds. Threshold comparisons use the mathematically equivalent N ≥ 3R² or N ≥ R² to avoid floating-point pi drift. These uncalibrated labels never adjust price or profitability.

## Pricing and demographics

Typed `PricingItem[]` supports explicit units, variable costs, monthly volume, allocated monthly fixed costs, overhead weights, target-margin range, source and version. A shared fixed-cost total is required. Weights must sum to 1 and allocations must match that total; invalid assumptions return missing-input guidance without numeric prices.

For valid planning assumptions:

```text
overhead/unit = allocated monthly fixed cost / monthly volume
planning cost/unit = variable unit cost + overhead/unit
selling price = planning cost/unit / (1 − target selling-price margin)
unit contribution = displayed target price − variable unit cost
operating break-even volume = allocated monthly fixed cost / unit contribution
```

The target margin is the midpoint of the supplied min/max margin range. Decimal arithmetic and the existing INR half-up paise rounding are used. Volume ≤ 0 yields no price. Contribution ≤ 0 yields no break-even. Per-item break-even uses allocated overhead; aggregate mixed-product break-even is withheld without a sales mix.

Current production catalog data has no structured unit costs/volumes/margins, so normal API results correctly return `INSUFFICIENT_PRICING_ASSUMPTIONS`, empty items and explicit missing assumptions. The numeric engine is tested with explicit fixtures; no production amounts or products were invented. Valid supplied internal assumptions produce `CALCULATED_FROM_PLANNING_ASSUMPTIONS`.

Always explicit today: `LOCAL_PRICE_DATA_UNAVAILABLE`, `VERIFIED_DATA_UNAVAILABLE`, `PURCHASING_POWER_DATA_UNAVAILABLE`, null purchasing-power adjustment, null competitor-price adjustment. District/taluka names and demo activity signals never influence pricing.

## API and persistence

```http
POST /api/v1/business-analysis
Authorization: Bearer <token>
Content-Type: application/json

{"financial_analysis_id":"<owned UUID>","radius_km":5}
```

Radius is strict integer 1–10; extra fields are forbidden, including demo market IDs, supplied evidence, financial calculations, coordinates, prices and threats. Success returns 201. `GET /api/v1/business-analysis/{id}` returns the owned immutable result; foreign/missing records return the same 404. No list/history endpoint exists.

Response: `id`, `created_at`, `business`, `profile_context`, `financial_context`, `market_context`, structured SWOT quadrants, `local_threats`, competition metrics/records/quality, pricing status/items/assumptions, `evidence`, and `quality` with source/freshness/section states/warnings/rule versions/context hash.

Financial invariants and versions reuse SchemeService validation, followed by setup-alignment and catalog-cost compatibility checks. Profile/source changes during provider work return a controlled 409. Module 14A geocode errors, throttling and provider failures retain its controlled behavior. Stale fallback retains observation dates and suppresses current competition classification. No usable real evidence means no saved complete analysis.

Migration `20260908_09_create_business_analyses.py`, revision `20260908_09`, parent `20260908_08`, adds `business_analyses`: UUID, owner, business, financial source, creation time, checked radius, profile/location fingerprints, rule versions, catalog/context hashes, JSONB evidence/context and result snapshots. Owner index and foreign keys are included. ORM and PostgreSQL trigger guards reject updates. Normalized POI values are captured, not raw Overpass responses, so cache refresh cannot rewrite historical evidence. Account deletion can still cascade deletion of owned snapshots.

## Frontend and flow

`/business-analysis` replaces the Business Health sidebar placeholder; `/business-health` redirects. No duplicate sidebar concept was added. Direct navigation finds the latest financial snapshot for the active proposed business. The Scheme panel has a Continue to Business Analysis link carrying the saved financial ID. Saved results use `analysis_id` in the URL and reload through owner-scoped GET. Changed URL source identity remounts page state to prevent incompatible results remaining visible.

Sections: Business Overview, four SWOT cards, Local Threats, Competitor Mapping, Pricing & Product Market Value, Evidence & Data Quality. Source age, live/cache/stale state, provisional labels, mitigations, evidence links, assumptions and limitations are visible. The existing `EvidenceMap` renders the centre, selected-radius circle, direct/related markers, attribution and accessible text list, retaining sidebar-resize behavior. No new map library or packages were added. Module 15 uses a 60-second request timeout without changing shared defaults.

## Validation

Created test files: `backend/tests/test_business_analysis_engines.py` and `backend/tests/test_business_analysis.py`.

Coverage includes all eight business risks; exact pressure thresholds and bands; 1/10 km density normalization; strict radius/extra-field validation; ownership; missing/mismatched proposed business; financial integrity/version and catalog costs; current and mid-request profile changes; unknown optional data; zero/stale/weak/incomplete evidence; pricing formula/margin/rounding/volume/allocation; source-fingerprint reproducibility; immutable database snapshots; and saved evidence surviving POI updates. Provider responses are mocked.

Results:

| Check | Result |
| --- | --- |
| Targeted Module 15 | **66 passed in 2.12 s** |
| Full backend suite | **360 passed in 15.33 s** |
| Existing frontend state tests | **5 passed** |
| `alembic upgrade head` on configured application DB | **Passed: 20260908_08 → 20260908_09** |
| Isolated validation DB migrations/seeds | **Passed** |
| `npm run lint` | **Passed** |
| `npm run build` | **Passed** |
| `git diff --check` | **Passed** |

Backend commands ran from `backend/`:

```bash
.venv/bin/alembic upgrade head
DATABASE_URL=postgresql+psycopg://abhayvijaysonone@localhost/udyammitra_module15_validation_20260908 .venv/bin/python -m pytest tests/test_business_analysis_engines.py tests/test_business_analysis.py -q --tb=short
DATABASE_URL=postgresql+psycopg://abhayvijaysonone@localhost/udyammitra_module15_validation_20260908 .venv/bin/python -m pytest -q --tb=short
```

Root commands: `node --test tests/nearbyState.test.mjs`, `npm run lint`, `npm run build`, `git diff --check`.

The former temporary test cluster was unavailable. The existing application database was migrated additively; no existing database was recreated. Tests used a newly created separate validation database on the existing server. One test invocation from the repository root failed because backend authentication environment configuration was not loaded; rerunning from `backend/` passed. An optional compileall attempt hit the sandbox's Python cache path restriction; actual imports and all tests subsequently passed.

Optional live smoke: **not run**. Automatic approval review rejected the request because it would send the temporary profile's locality-derived location to Nominatim and Overpass. No live provider request occurred. Explicit approval for that data and those destinations is required to perform the optional check.

Remaining build warning: minified JavaScript bundle 763.70 kB (226.33 kB gzip), above Vite's 500 kB warning threshold. No browser automation tools were available; browser interaction was not claimed as tested.

## Manual browser checks

1. Start the backend and frontend using existing configuration. The configured local application database migration has already succeeded in this session.
2. Sign in, select a proposed business in Profile and save a financial analysis for that same business.
3. Check financing, then use Continue to Business Analysis. Verify business/margin/project capacity and default 5 km.
4. Generate analysis. Inspect loading/errors, SWOT, threat kinds/severity/mitigation, counts, nearest/average/density, distance bands and source timestamps.
5. Open evidence links and threat links; check the supporting values and versions. Pricing should honestly show missing assumptions for the current catalog.
6. Inspect the centre/circle/markers/list/OSM attribution. Resize the window and collapse/expand the sidebar.
7. Change radius, generate a new result and reload its analysis URL. The saved snapshot must retain its original evidence and radius.
8. Visit `/business-health`; verify redirection to Business Analysis. Visit Business Analysis directly; it should use the latest financial plan for the proposed business.
9. Change proposed business or catalog-linked financial source; verify controlled mismatch guidance. Change profile own capital; verify the budget inconsistency warning rather than silent financial recalculation.
10. Check unavailable/ambiguous locality errors. Inspect a no-mapped-result case: it must not claim no real competitors or unmet demand. Server stale/incomplete behavior is covered by mocked tests; browser offline mode alone is not a server stale-cache test.
11. Check existing Market Analysis, Opportunities, Financial Plan and Scheme flows for regressions. Do not repeatedly query public providers for testing.

## Limitations, deferred work and next module

OSM coverage and production/rental mappings remain limited; representative centres and possible duplicate establishments remain. Competition classifications are uncalibrated. Skills/resources are self-reported, with broad aliases tentative. Existing-business matching is deliberately conservative. Qualitative catalog updates use the current catalog hash; legacy financial snapshots do not contain a full historic knowledge hash. Pricing remains unavailable without explicit structured assumptions; there is no editable scenario or external price source. Output is deterministic English; dynamic multilingual output is deferred. No demographic, demand, profitability, repayment or purchasing-power inference is manufactured.

Deferred Module 15 enhancements: curated/priced assumption templates with provenance, calibrated business-specific competition thresholds, richer explicit existing-business linkage, and browser automation when tooling is available. These are not prerequisites to the completed first pass.

Recommended next module: **Module 16 — AI Advisor**, consuming owned Module 15 snapshots as evidence while keeping all calculations and classifications authoritative in the deterministic backend. RAG, unified reports, PDF, history UI and repayment remain separate future work.
