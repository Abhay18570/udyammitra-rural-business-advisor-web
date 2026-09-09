# Module 14A completion report

## Resumed implementation

The existing work already contained provider integration, separate live POI/cache structures, conservative business mappings, real-evidence UI, Leaflet bounds/resize handling, location correction states, and completed-query caching. This continuation preserved that work and unrelated existing financial, scheme, and sidebar changes.

Completed now: mocked provider/API tests, PostGIS boundary/schema tests, cache integrity and regression coverage, cancellable provider deadlines, bounded connection retries, cross-worker geocoder cooldown refinement, fresh ORM cache reads, catalog retry handling, hidden-map resize protection, configuration verification, documentation, migration execution, full validation, and one live smoke test. Demo and feasibility scoring remain independent.

## Exact Module 14A files

New files (including files already started before continuation):

```text
backend/alembic/versions/20260907_07_create_hyperlocal_caches.py
backend/app/engines/nearby_market_engine.py
backend/app/models/market_cache.py
backend/app/models/market_poi.py
backend/app/osm_business_rules.py
backend/app/providers/__init__.py
backend/app/providers/errors.py
backend/app/providers/http.py
backend/app/providers/geocoding.py
backend/app/providers/overpass.py
backend/app/repositories/nearby_market_repository.py
backend/app/schemas/nearby_market.py
backend/app/services/geocoding_service.py
backend/app/services/nearby_market_service.py
backend/app/utils/spatial.py
backend/tests/test_geocoding.py
backend/tests/test_overpass.py
backend/tests/test_nearby_market_engine.py
backend/tests/test_nearby_market.py
src/types/nearbyMarket.ts
src/features/marketAnalysis/NearbyBusinessEvidence.tsx
MODULE14A_IMPLEMENTATION.md
```

Modified files for this module:

```text
README.md
backend/.env.example
backend/app/core/config.py
backend/app/models/__init__.py
backend/app/repositories/market_repository.py
backend/app/api/v1/endpoints/market.py
src/services/marketService.ts
src/features/marketAnalysis/MarketAnalysisPage.tsx
src/features/marketAnalysis/MarketMap.tsx
src/i18n/translations.ts
src/index.css
```

Other changes visible in the working tree predate this module and were preserved.

## Database and providers

Migration `20260907_07_create_hyperlocal_caches.py`, parent `20260904_06`, adds:

| Table | Responsibility |
| --- | --- |
| `market_pois` | Normalized OSM records; geography(Point,4326), GiST index, unique provider/type/external ID, tags/address and fetch time |
| `geocoding_cache` | Location fingerprint, resolution state/provenance, fetch and expiry timestamps |
| `nearby_query_cache` | Complete query coverage, POI membership (including empty arrays), centre/provider/mapping version and expiry |
| `provider_request_state` | Database-backed provider/query leases, cooldown and concurrency coordination |

Existing demo tables and migration history are unchanged. `alembic upgrade head` successfully upgraded the existing isolated PostgreSQL/PostGIS database to `20260907_07`; a second run was successful and made no further migration. No database was recreated. The configured application database at localhost:5432 was unavailable; validation used the existing test cluster at localhost:55432. Apply the migration to your application database when it is running.

Geocoding derives village, taluka, district, state and a location fingerprint from the authenticated profile. It tries the full locality query, then village/district/state/India. Nominatim requests restrict country to India and validate country, state, district and locality precision. Unicode text is normalized. One unambiguous acceptable locality is required. Existing profile coordinates are neither used as an override nor overwritten. Ambiguous/coarse results return `409 LOCATION_CONFIRMATION_REQUIRED`; no accepted match returns `422 LOCATION_NOT_RESOLVED`. Interactive confirmation is deferred; the user corrects the profile and retries.

Overpass receives only the resolved centre and backend-owned OSM rules, querying a 10.1 km candidate envelope. Nodes and way/relation centres are normalized, deduplicated by element type and ID, bounded by payload/element limits, and classified. Missing names receive a fallback. Partial/malformed responses do not become successful coverage. No credentials, identity or financial information is sent to either provider. Requests have deadlines; only connection-establishment failures receive one bounded retry. HTTP throttling is not automatically retried.

## Exact business mappings

Within a group, `+` means all tags are required; semicolons separate alternatives. Direct evidence takes precedence over related evidence. Closed/disused/construction lifecycle tags are conservatively excluded.

| Business slug | Direct competitor tags | Related-business tags |
| --- | --- | --- |
| `tailoring-alteration` | `shop=tailor`; `craft=tailor`; `craft=dressmaker` | `shop=clothes` |
| `mobile-repair-accessories` | `shop=mobile_phone` + `mobile_phone:repair=yes`; `craft=electronics_repair` + `electronics_repair=phone` | `shop=mobile_phone` |
| `kirana-general-store` | `shop=convenience`; `shop=general` | `shop=supermarket`; `shop=grocery` |
| `dairy-enterprise` | `landuse=farmyard` + `produce=milk` | `shop=dairy`; `industrial=dairy` |
| `poultry-enterprise` | `landuse=farmyard` + `produce=eggs`; `landuse=farmyard` + `produce=poultry` | `shop=butcher` + `butcher=poultry` |
| `flour-mill` | `man_made=works` + `product=flour`; `craft=mill` + `product=flour` | `craft=mill` |
| `food-processing-unit` | None: product definition is insufficient for direct evidence | `industrial=food`; `man_made=works` + `product=spices`; `man_made=works` + `product=pickles` |
| `agri-equipment-rental` | `shop=agrarian` + `agrarian=machinery` + `rental=yes` | `shop=agrarian` + `agrarian=machinery` |

The last five businesses carry weak-mapping warnings. Related evidence never increases direct competitor totals. Registry version: `osm-business-v1`.

PostGIS `ST_DWithin` and spheroidal `ST_Distance` on geography are authoritative, with longitude/latitude point order. Unrounded distances `0 <= d <= 5000` are `WITHIN_5_KM`; `5000 < d <= 10000` are `BETWEEN_5_AND_10_KM`; larger distances are excluded. Only displayed kilometres are rounded.

## API, UI and cache behavior

Authenticated `POST /api/v1/market/nearby` accepts only:

```json
{"business_slug":"tailoring-alteration"}
```

Extra fields are rejected with 422. Missing profile location returns 409; unknown/inactive business returns 404. Provider failures are sanitized 503/504 responses, or 429 with retry guidance where available.

The response contains `business`, `location` (resolved coordinates and provenance), `radius`, `summary`, `competitors`, `related_businesses`, `source`, and `quality`. Summary fields are `competitors_within_5km`, `competitors_between_5_and_10km`, `total_direct_competitors`, and nullable `nearest_direct_competitor`. Each POI includes source ID/type, name, coordinates, evidence rule/tags, distance, band and fetch time. The full contract is in `backend/app/schemas/nearby_market.py`.

Market Analysis exposes Real Nearby Business Evidence separately from demonstration scoring. It supports catalog selection/retry, loading, errors, profile correction, empty results, direct/related lists, nearest competitor, counts, evidence, freshness labels and coverage warnings. English, Hindi and Marathi labels are included. Profile changes invalidate visible evidence on the implemented refresh/focus checks. Empty wording is: “No mapped direct competitors were found in the available OpenStreetMap data.”

The existing Leaflet map displays the centre, 5 km and 10 km circles, direct/related markers, safe text popups, OSM attribution and a text list. It refits bounds for changed results and uses ResizeObserver for sidebar/container resizing. No additional map library was added. Nearby requests alone use a 60-second frontend timeout; the shared default remains 10 seconds.

Complete new searches return `LIVE / FRESH_FETCH`; fresh hits return `CACHE / FRESH_CACHE`; eligible fallback returns `CACHE / STALE_CACHE` with a warning and original timestamps. Geocoding success lasts 30 days, negative/ambiguous results one hour, complete nearby results 24 hours and empty results one hour. Stale fallback requires matching complete coverage no older than seven days. POIs alone do not establish coverage. Refresh atomically replaces membership and retains shared POIs; failed/partial refresh preserves the previous complete cache. Mapping-version changes invalidate coverage. Demo data is never substituted for live results.

## Local environment

Existing database/auth configuration is still required. These backend-only settings have defaults and are documented in `backend/.env.example`; no new frontend environment variables or packages are required:

```dotenv
NOMINATIM_BASE_URL=https://nominatim.openstreetmap.org
OSM_USER_AGENT=UdyamMitra-SIH/0.1 (locality and business evidence)
GEOCODING_TIMEOUT_SECONDS=8
GEOCODING_MIN_INTERVAL_SECONDS=1.1
GEOCODING_CACHE_TTL_SECONDS=2592000
GEOCODING_NEGATIVE_CACHE_TTL_SECONDS=3600
OVERPASS_BASE_URL=https://overpass-api.de/api/interpreter
OVERPASS_TIMEOUT_SECONDS=25
OVERPASS_QUERY_TIMEOUT_SECONDS=20
OVERPASS_MAX_RESPONSE_BYTES=5000000
OVERPASS_MAX_ELEMENTS=5000
OVERPASS_MAX_CONCURRENT_REQUESTS=1
NEARBY_REQUEST_TIMEOUT_SECONDS=50
NEARBY_CACHE_TTL_SECONDS=86400
NEARBY_EMPTY_CACHE_TTL_SECONDS=3600
NEARBY_STALE_MAX_AGE_SECONDS=604800
```

## Validation results

Backend commands ran from `backend/` using the existing isolated database. The exact database override was `DATABASE_URL=postgresql+psycopg://module12_test@127.0.0.1:55432/postgres`.

```bash
DATABASE_URL=postgresql+psycopg://module12_test@127.0.0.1:55432/postgres .venv/bin/alembic upgrade head
DATABASE_URL=postgresql+psycopg://module12_test@127.0.0.1:55432/postgres .venv/bin/python -m pytest tests/test_geocoding.py tests/test_overpass.py tests/test_nearby_market_engine.py tests/test_nearby_market.py tests/test_market.py tests/test_feasibility.py -q --tb=short
DATABASE_URL=postgresql+psycopg://module12_test@127.0.0.1:55432/postgres .venv/bin/python -m pytest -q --tb=short
```

- Migration: passed, including repeated upgrade-to-head.
- Targeted suite: **121 passed in 9.95 seconds**.
- Full backend suite: **267 passed in 11.95 seconds**, including financial and scheme regressions.
- Root `npm run lint`: passed without warnings.
- Root `npm run build`: passed. Vite warns that the JS bundle is 750.85 kB minified (223.42 kB gzip), above its 500 kB threshold.
- Root `git diff --check`: passed.
- Automated provider tests use mocks, never live public providers.
- One live authenticated TestClient smoke request, after the mocked suite: **HTTP 200, LIVE / FRESH_FETCH** for Mankoli/Bhiwandi/Thane/Maharashtra and Tailoring. It returned 0 mapped direct competitors within 5 km and 2 between 5–10 km; nearest 7.74 km. Temporary user/profile/cache writes were rolled back. No repeated live lookup was performed.

New test files cover geocoding success/fallback/Unicode/context/ambiguity/coarse/no match/timeout/throttling/malformed data/fingerprint/configuration; Overpass element types/deduplication/names/coordinates/errors/limits/retries/deadlines; all eight mappings/lifecycle exclusions/boundaries; and authenticated API/privacy/PostGIS/schema/cache expiry/empty/stale/failure/membership/version behavior. Exact test function inventory follows below.

## Manual browser checks and remaining limitations

1. Start your existing PostgreSQL/PostGIS application database; from `backend/`, activate `.venv`, run `alembic upgrade head`, and start `uvicorn app.main:app --reload`. Start the frontend with root `npm run dev`.
2. Sign in and save a complete profile locality (for example Mankoli, Bhiwandi, Thane, Maharashtra, 421302).
3. Open Market Analysis, select Tailoring and click Find Nearby Businesses. Confirm loading then counts, nearest, evidence and source/fetch time. Actual OSM counts can change.
4. Check both map circles, centre, markers, readable popups, attribution and the text list. Collapse/expand the sidebar, resize the window and check a narrow mobile viewport.
5. Repeat the same search once to inspect CACHE. Check related businesses are separate from direct totals.
6. Edit the profile locality, return to Market Analysis and verify old evidence clears; retry. An unresolvable or ambiguous locality should show correction guidance, never a silently selected centre.
7. Inspect a successful empty result if encountered: use the exact mapped-data wording above. Check English/Hindi/Marathi labels.
8. Use browser offline mode to check a recoverable UI error, then restore connectivity and retry. Backend stale-provider failure cases require controlled backend failure/expiry and are covered by automated tests; browser offline mode alone does not exercise server stale fallback.
9. Open the demonstration disclosure and run existing demo analysis/feasibility to check their separate labels and behavior.

Browser interaction was not executed here; no browser automation tooling was available. All compilation and backend checks passed. OSM is incomplete, locality/way/relation centres are approximate, distinct OSM elements can represent one establishment, and strict administrative/spelling matching can require profile correction. Interactive candidate confirmation and cache cleanup automation remain deferred. No broader POIs, live scoring, pricing, AI/RAG, repayment or reporting work was added.

Recommended next Module 14 work: authenticated geocode candidate confirmation with backend-issued provenance, then cache retention/provider operational monitoring and deduplication/coverage improvements before extending the evidence categories.

## Exact added test functions

backend/tests/test_nearby_market.py:def test_api_live_cache_counts_and_privacy(client, db_session, osm):
backend/tests/test_nearby_market.py:def test_empty_search_is_cached(client, db_session, osm):
backend/tests/test_nearby_market.py:def test_failed_refresh_preserves_cache_and_returns_stale(client, db_session, osm, failure):
backend/tests/test_nearby_market.py:def test_refresh_replaces_membership_without_deleting_shared_pois(client, db_session, osm):
backend/tests/test_nearby_market.py:def test_mapping_version_invalidates_cache(client, db_session, osm, monkeypatch):
backend/tests/test_nearby_market.py:def test_unavailable_without_usable_cache_is_not_empty_success(client, db_session, osm, old_cache):
backend/tests/test_nearby_market.py:def test_auth_profile_and_business_validation(client, db_session, osm):
backend/tests/test_nearby_market.py:def test_forbidden_client_fields(client, osm, field):
backend/tests/test_nearby_market.py:def test_location_resolution_states(client, db_session, osm, geocoding, expected_status, code):
backend/tests/test_nearby_market.py:def test_fallback_unicode_and_changed_fingerprint(client, db_session, osm):
backend/tests/test_nearby_market.py:def test_postgis_boundaries_and_coordinate_order(db_session, meters, band):
backend/tests/test_nearby_market.py:def test_cache_schema_and_spatial_index(db_session):
backend/tests/test_nearby_market.py:def test_provider_slots_are_exclusive_and_released(db_session):
backend/tests/test_nearby_market.py:def test_partial_without_cache_never_saves_query(client, db_session, osm):
backend/tests/test_nearby_market.py:def test_cached_pois_do_not_prove_query_coverage(client, db_session, osm):
backend/tests/test_nearby_market.py:def test_untrusted_profile_coordinates_are_not_used_or_overwritten(client, osm):
backend/tests/test_nearby_market.py:def test_geocoder_outage_is_controlled(client, db_session, osm):
backend/tests/test_nearby_market.py:def test_registry_matches_actual_seeded_catalog(db_session):
backend/tests/test_nearby_market_engine.py:def test_radius_boundary_before_rounding(distance, expected):
backend/tests/test_nearby_market_engine.py:def test_invalid_distance(distance):
backend/tests/test_nearby_market_engine.py:def test_mapping_evidence(slug, tags, classification):
backend/tests/test_nearby_market_engine.py:def test_catalog_coverage_and_unknown_mapping():
backend/tests/test_overpass.py:def test_node_way_relation_duplicates_and_missing_name():
backend/tests/test_overpass.py:def test_invalid_record_count(element):
backend/tests/test_overpass.py:def test_invalid_or_partial_payload(payload):
backend/tests/test_overpass.py:def test_element_limit():
backend/tests/test_overpass.py:def test_size_limit_and_no_auth_forwarding():
backend/tests/test_overpass.py:def test_query_is_backend_owned_and_bounded():
backend/tests/test_overpass.py:def test_connection_retry_is_bounded():
backend/tests/test_overpass.py:def test_rate_limit_is_not_retried():
backend/tests/test_overpass.py:def test_real_transport_cancels_at_total_deadline():
backend/tests/test_geocoding.py:def test_success_and_minimal_query():
backend/tests/test_geocoding.py:def test_malformed_provider_response(raw):
backend/tests/test_geocoding.py:def test_timeout():
backend/tests/test_geocoding.py:def test_throttle():
backend/tests/test_geocoding.py:def test_conservative_context(address, precision, expected):
backend/tests/test_geocoding.py:def test_unicode_and_changed_fingerprint():
backend/tests/test_geocoding.py:def test_configuration_guards(overrides):
