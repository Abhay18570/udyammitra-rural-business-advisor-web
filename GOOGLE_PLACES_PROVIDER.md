# Optional Google Places nearby provider

The existing Overpass provider remains the default. Google Places API (New) is selected only by setting `NEARBY_MARKET_PROVIDER=google` in the backend environment and restarting FastAPI. There is no automatic fallback to Overpass and no frontend key/configuration change when switching providers.

## Architecture and configuration

`NearbyBusinessProvider` defines the shared fetch contract. `ProviderPolicy` chooses the implementation, mapping, provenance, warnings and cache identity. `GooglePlacesProvider` owns all Google request/normalization code. `OverpassProvider`, Nominatim geocoding, and the PostGIS distance and radius predicates remain in use. Module 15 still invokes Module 14 once and saves its result; its calculation engines are unchanged. Its source metadata now reflects the selected provider.

| Backend variable | Default / constraint |
| --- | --- |
| `NEARBY_MARKET_PROVIDER` | `overpass`; allowed: `overpass`, `google` |
| `GOOGLE_PLACES_API_KEY` | Empty example; backend-only `SecretStr`, excluded from settings repr |
| `GOOGLE_PLACES_BASE_URL` | `https://places.googleapis.com/v1/places:searchNearby`; other endpoints rejected to avoid forwarding the key |
| `GOOGLE_PLACES_TIMEOUT_SECONDS` | 15 seconds; greater than zero, at most 25 |
| `GOOGLE_PLACES_MAX_RESULTS` | 20; range 1–20 |

The existing local environment files were not modified by this implementation. No dependencies were added.

## Request and mappings

One server-side POST requests `includedTypes`, `maxResultCount`, `rankPreference: DISTANCE`, and `locationRestriction.circle` with the resolved latitude/longitude and selected radius in meters. Radius is exactly 1000/5000/10000 for the corresponding selections. No candidate-radius expansion is applied to Google. Google results remain candidates: PostGIS applies the existing exact `ST_Distance <= selected_meters` predicate with indexed `ST_DWithin` candidates.

Headers are `X-Goog-Api-Key`, `Content-Type: application/json`, and `X-Goog-FieldMask` with exactly:

```
places.id,places.displayName,places.location,places.primaryType,places.types,places.formattedAddress,places.businessStatus
```

The key is never included in the URL. No reviews, ratings, photos, opening hours, Text Search, or Google Geocoding calls are made. The mask is deliberately limited but does not imply the request is free: fields determine the applicable Nearby Search SKU.

The registry version is `google-types-20260908-v1`. Types were checked against Google's [Place Types (New)](https://developers.google.com/maps/documentation/places/web-service/place-types) and request parameters against [Nearby Search (New)](https://developers.google.com/maps/documentation/places/web-service/nearby-search).

| Catalog business | Direct types | Related types / limitation |
| --- | --- | --- |
| tailoring-alteration | `tailor` | `clothing_store` |
| mobile-repair-accessories | None | `cell_phone_store`, `electronics_store`; sales do not establish repair capability |
| kirana-general-store | `convenience_store`, `grocery_store` | `supermarket` |
| dairy-enterprise | None | `food_store`; broad retail context, not dairy production evidence |
| poultry-enterprise | None | `butcher_shop`; not poultry production evidence |
| flour-mill | None | No defensible structured mapping; no HTTP search |
| food-processing-unit | None | No defensible structured mapping; no HTTP search |
| agri-equipment-rental | None | No defensible structured mapping; no HTTP search |

Direct types take precedence. No business-name inference is used. Unexpected otherwise valid establishments remain `GENERIC_POI` in a separate `generic_pois` response list and never contribute to direct/related counts, nearest competitor, density, or map markers. Limited mappings emit `LIMITED_BUSINESS_MAPPING`; unsupported strategies also emit `NO_SUPPORTED_NEARBY_TYPES`. Every Google response emits `GOOGLE_RANKED_SUBSET`, including empty responses, because even fewer than the cap is not proof of exhaustive coverage. `complete_query` means a successfully handled provider response, not a complete census.

## Normalization, persistence and cache

Only normalized ID, name, coordinates, primary/type list, address, business status, classification, mapping version, and fetch time are persisted. Provider is `GOOGLE_PLACES`, external type `place`, coordinate kind `PLACE_LOCATION`. Type lists use a semicolon-separated string in the existing normalized tag dictionary. Non-operational places are excluded; malformed records cause controlled failure rather than poisoning a good cache. Duplicate Google IDs are deduplicated within a response. There is no cross-provider name matching.

Migration `20260908_10` changes only `market_pois.external_id` from bigint to varchar(255), preserving existing OSM IDs. The existing `(provider, external_type, external_id)` uniqueness constraint remains. OSM numeric tie ordering is retained. A downgrade requires removal/export of nonnumeric provider IDs first; the migration refuses invalid casts rather than deleting data.

Cache keys include provider, endpoint, centre, locality fingerprint, business, exact radius, mapping version, query strategy (including result cap/ranking), and field mask. No provider or radius can satisfy another's cache request. This version changes cache signatures, so existing cache rows are retained but old signatures are not reused on the first request after upgrade. Existing TTLs and stale fallback rules are reused: 24 hours normally, one hour empty, and at most seven days for stale fallback by default. A failed Google refresh may use only its own matching complete cache; otherwise it returns a controlled upstream error. It never silently calls Overpass.

**Storage limitation:** This implementation follows the requested existing persistent-cache and immutable-analysis architecture. Google's standard [Places policies](https://developers.google.com/maps/documentation/places/web-service/policies) restrict storage/caching of Places content, with place IDs exempt. Do not assume the existing cache TTLs or indefinite saved snapshots authorize retention of names, addresses and other Google content. Before using real Google data with persistent history, resolve the applicable storage permissions or implement a retention/snapshot design compatible with those terms. No live Google requests were used for this implementation or validation. Overpass remains the default.

## Failures and UI compatibility

Missing Google credentials produce `PROVIDER_NOT_CONFIGURED` (503). Timeouts return controlled 504 responses; throttling returns 429 with bounded retry guidance; other upstream HTTP/redirect/malformed/oversized responses use sanitized provider errors. Only connection establishment failures are retried once under the shared deadline. Partial results do not overwrite complete cache membership. The HTTP client never follows redirects with the key.

Frontend edits are limited to accepting Google identity/coordinate enums and displaying the evidence provider, including empty results and info-window text. Google Maps markers, circle, camera, resizing and key loading are unchanged. No frontend discovery calls were added. Saved Module 15 values and engines remain unchanged; quality warnings and source metadata are retained in saved evidence.

## Local manual verification

1. Keep your existing database/JWT configuration and both local API keys. From the repository root run `cd backend`, `source .venv/bin/activate`, and `alembic upgrade head` against your application database. The automated migration run used an isolated test database; it did not upgrade your application database.
2. In `backend/.env`, add or update `NEARBY_MARKET_PROVIDER=google`. Keep the existing backend-only `GOOGLE_PLACES_API_KEY`; do not move it to a Vite variable. Resolve the storage limitation above before requesting real data.
3. Stop FastAPI with Ctrl+C and restart with `uvicorn app.main:app --reload`.
4. In a second terminal at the repository root, run `npm run dev`. Open the Vite URL, sign in, and open Market Analysis.
5. Select Tailoring and 5 km, then explicitly click **Find Nearby Businesses**. Inspect the `/api/v1/market/nearby` response in browser Network tools: expect `source.provider=GOOGLE_PLACES`, `radius.selected_meters=5000`, and ranked-subset coverage warning. The backend key must not appear in browser requests or responses.
6. Verify the Google map, centre, selected circle, and marker roles still work. The evidence label and marker popups must say Google Places. Compare direct/related counts and nearest competitor with the backend response.
7. Repeat for 1 km and 10 km: changing radius clears old evidence without searching automatically. Returned records must have `distance_meters <= radius.selected_meters`. Exact-on-boundary and 1 cm outside behavior is also covered by mocked PostGIS regression tests.
8. Try mobile repair and dairy/poultry: related outlets must not be counted as direct production/repair competitors. Flour mill, food processing and agricultural rental return explicit unsupported-strategy warnings rather than an unfiltered Google search.
9. For a zero-result response, verify the centre/circle remain and the UI says no mapped direct competitors were found, without asserting there are no real competitors.
10. Create Business Analysis from matching financial/profile inputs. Verify Google provenance and coverage warnings, and compare counts/density/nearest with its saved evidence. Reload the saved analysis: no independent nearby discovery should occur.
11. Set `NEARBY_MARKET_PROVIDER=overpass`, completely restart FastAPI, and repeat the same business/radius. Expect OpenStreetMap/Overpass provenance, existing Overpass warnings, and no reuse of Google results. The map visualization remains Google Maps. No frontend environment changes are needed.
12. Provider failures should be checked using mocked tests; do not deliberately generate repeated billable failures. Without a valid matching cache, a Google failure must return a controlled error; with an eligible old matching cache it may return STALE CACHE.

## Validation commands

Run against an isolated migrated and seeded PostgreSQL/PostGIS test database, overriding the backend key with a dummy test value and provider with `overpass`. Provider tests use mock transports only.

```
python -m pytest tests/test_google_places.py tests/test_google_nearby.py tests/test_overpass.py tests/test_nearby_market.py tests/test_business_analysis.py tests/test_business_analysis_engines.py -q
python -m pytest -q
```

From the root: `python -m compileall backend/app`, `npm run lint`, `npm run build`, `node --test tests/*.test.mjs`, and `git diff --check`. On this machine Python's default bytecode cache is outside the writable workspace; compilation used `PYTHONPYCACHEPREFIX=/tmp/udyam-places-pycache`.

Live Google billing/referrer/authentication behavior and manual browser checks remain unverified. The existing Vite JavaScript chunk warning remains; unrelated bundle optimization was not performed.

## Implementation inventory and recorded results

Created:
- `backend/app/google_places_rules.py`
- `backend/app/providers/nearby.py`
- `backend/app/providers/google_places.py`
- `backend/alembic/versions/20260908_10_provider_place_ids.py`
- `backend/tests/test_google_places.py`
- `backend/tests/test_google_nearby.py`
- `GOOGLE_PLACES_PROVIDER.md`

Modified existing files (relative to the start of this task, including files already untracked in the working tree):
- `backend/.env.example`
- `backend/app/core/config.py`
- `backend/app/models/market_poi.py`
- `backend/app/repositories/nearby_market_repository.py`
- `backend/app/schemas/nearby_market.py`
- `backend/app/services/nearby_market_service.py`
- `backend/app/services/business_analysis_service.py` (source metadata only)
- `backend/tests/test_nearby_market.py` (mapping-version patch target and string-ID fixture)
- `src/types/nearbyMarket.ts`
- `src/features/marketAnalysis/evidenceMapModel.ts`
- `src/features/marketAnalysis/MarketMap.tsx` (evidence-provider label only)
- `src/features/marketAnalysis/NearbyBusinessEvidence.tsx` (provider/source wording only)
- `src/features/businessAnalysis/BusinessAnalysisPage.tsx` (pass evidence provider to label)
- `tests/evidenceMap.test.mjs`
- `README.md`

Recorded validation:
- Targeted backend suite: **188 passed**.
- Full backend suite after final backend fixes: **403 passed**.
- Migration: `alembic upgrade head` passed on isolated `udyam_places_test`; string-ID conversion/round-trip smoke test passed. Application database was not migrated.
- `compileall backend/app`: passed with writable temporary bytecode cache prefix.
- Frontend tests: **13 passed**.
- `npm run lint`: passed.
- `npm run build`: passed; existing warning for a **662.75 kB** JavaScript chunk remains.
- `git diff --check`: passed.
- Secret scan: actual backend key absent from tracked/nonignored source files and frontend build. No live API key was printed.
- No new dependencies, live provider requests, local environment edits, Overpass removal, PostGIS calculation changes, map rendering redesign, or next-module implementation.
