Module 14 free-text market discovery — implementation report

Market Analysis accepts arbitrary business ideas and searches Google Places Text Search when `NEARBY_MARKET_PROVIDER=google`. The existing eight-business catalog, financial calculations, Overpass provider, and catalog analysis rules remain in place.

1. **Audit findings.** Ran `git status`, `git diff --stat`, and `git diff` before edits. The workspace already contained extensive tracked and untracked changes. Inspected the Market Analysis page, control/reducer, API client/types, translations, evidence map, provider abstraction/configuration, Google Nearby Search, Overpass, repository/cache signatures, normalization, spatial helpers, Module 15 service/contracts/tests, and migrations. The mandatory selector and request used only catalog slugs. The evidence list always displayed OSM tags/links, even for Google. Migration `20260908_10` only changes external IDs to strings; no later migration exists. Critically, Google content was still persisted in `market_pois`, query caches, and Module 15 snapshots; a transient candidate path did not exist.

2. **Behavior replaced.** Removed the mandatory catalog selection from the real nearby-evidence flow. The separate demonstration analysis and all other catalog selectors are retained.

3. **Frontend input.** A controlled text input accepts 2–200 characters after trimming/collapsing whitespace. Blank/one-character values cannot submit. Radius remains an integer from 1 through 10, default 5. Backend independently validates both fields.

4. **Suggestions.** Native `datalist` suggestions use existing catalog names. Loading suggestions is optional and cannot prevent arbitrary typing/searching. Exact catalog name/slug matches are resolved by the backend. No catalog entries are created, and broad synonyms never silently establish catalog identity.

5. **API contract.** Authenticated `POST /api/v1/market/nearby` accepts `{"business_query":"Tea Stall","radius_km":3}`. `business_slug` remains accepted for legacy callers. At least one intent is required. If both are supplied, the query must exactly match the specified active catalog entry. Responses add `business_query` and nullable `matched_catalog_business_slug`; `business.id`/`business.slug` are null for unmatched ideas. Existing radius/location/summary/competitor/related/generic/source/quality contracts remain. Query capitalization and meaning are retained after whitespace cleanup.

6. **Google implementation.** Added `GooglePlacesProvider.fetch_text`. Free-text requests use Text Search, including arbitrary production, repair, and rental queries. Legacy slug-only Google requests retain Nearby Search and its existing classification rules. All Google evidence now uses transient storage behavior.

7. **Endpoint and request.** The backend posts to `https://places.googleapis.com/v1/places:searchText`, using `X-Goog-Api-Key`, `X-Goog-FieldMask`, and `Content-Type: application/json`. The configured URL must exactly match the official endpoint. The key is never placed in the URL or frontend payload. Request shape:

   ```json
   {
     "textQuery": "Tea Stall",
     "pageSize": 20,
     "locationBias": {
       "circle": {
         "center": { "latitude": 19, "longitude": 73 },
         "radius": 3000
       }
     }
   }
   ```

   Request parameters and pagination follow the [official Text Search reference](https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places/searchText).

8. **Field mask.** `places.id,places.displayName,places.location,places.primaryType,places.types,places.formattedAddress,places.businessStatus,nextPageToken`. No reviews, photos, ratings, routes, or opening-hours fields are requested.

9. **Location/radius.** Uses Module 14's existing saved-profile locality resolution: village/taluka/district/state are geocoded through the established location cache/provenance flow. Existing unverified profile coordinate fields remain untrusted and untouched. Google receives the resolved centre and selected radius multiplied by 1,000. Circle bias discovers candidates and can return points outside the circle; PostGIS decides inclusion.

10. **Pagination/limits.** `GOOGLE_PLACES_TEXT_MAX_PAGES=2` by default, configurable from 1–3. Existing `GOOGLE_PLACES_MAX_RESULTS` controls page size (maximum 20): default at most 40 candidates, hard configured maximum 60 before deduplication/filtering. Only page tokens change between calls. Duplicate place IDs are removed; malformed/repeated tokens cause controlled errors. No extra subdivision searches or unbounded pagination. Shared request deadlines/timeouts/rate limits remain. A failed page does not produce a misleading successful partial analysis.

11. **PostGIS filtering.** Added `spatial_candidates`, using an SQL `VALUES` relation with transient indices/coordinates. It reuses the unchanged geography helpers and predicates: `ST_DWithin(..., radius + 0.001)` for candidates and unrounded spheroidal `ST_Distance(...) <= radius` for final inclusion. Coordinates remain longitude/latitude in PostGIS point construction. Only display kilometres are rounded. Tests cover exact boundaries and points 0.01 metres inside/outside at 1, 5, and 10 km.

12. **Normalization/synonyms.** `business_query_rules.py` defines `business-query-v1`. Whitespace normalization never rewrites the Google search intent. Small alias groups cover kirana/grocery, mobile/phone repair, tailor/alterations, medical/pharmacy/chemist, beauty parlour/salon, tea stall/shop, and hardware shop/store. Some kirana aliases also cover Devanagari. This is intentionally not a comprehensive multilingual taxonomy.

13. **Classification.** DIRECT requires all meaningful query tokens in the name, an explicit synonym intent in the name, a known direct primary category, or an exact meaningful query/primary-type match. RELATED uses known adjacent categories or partial meaningful name overlap. Everything else is GENERIC/uncertain. More specific unknown phrases do not inherit a broader alias's direct category. Retail electronics types alone do not prove mobile repair. No LLM, confidence probability, or fabricated score is used. Each result includes a versioned matching-rule reason.

14. **Google normalization.** Returns provider `GOOGLE_PLACES`, place ID, name, transient coordinates, primary/types/status tags, formatted address, classification, fetched time, and exact PostGIS distance. Closed businesses are excluded; malformed candidates cause a controlled failure rather than silent undercounting. Raw response objects never enter the API response or durable storage.

15. **Storage safety.** Google requests bypass durable query/POI caching, including slug-only requests. The repository rejects any attempt to send Google content through `save_query`. Only hashed request identity and provider lease coordination are written by this search path; even place IDs are currently kept request-local. Responses carry `Cache-Control: no-store`; Google UI does not show a cache-expiry label. No stale Google content fallback exists. Existing historical/cache rows from prior implementations were not purged; cleanup and policy-safe history remain separate work. Database/provider infrastructure logging must also avoid retaining request parameters.

16. **Provider-aware UI.** Google records show name, exact distance, classification, Google Places source, live address, and a Google Maps link. Overpass records retain source labels, matched tags, and OSM links. Generic evidence is shown as uncertain and appears on the existing map with its own neutral marker label.

17. **OSM wording removed for Google.** Google list entries contain neither OSM tags nor OSM links. Links use `https://www.google.com/maps/search/?api=1&query=<encoded-name>&query_place_id=<encoded-id>`, following [Google's documented Maps URL format](https://developers.google.com/maps/documentation/urls/get-started). Names and IDs are encoded, not interpolated as raw URL syntax.

18. **Overpass retained.** `NEARBY_MARKET_PROVIDER=overpass|google` is unchanged. Overpass still uses its catalog mappings/cache/provider and exact spatial logic. Free text that exactly matches a catalog name/slug works with Overpass; other ideas receive localized `OVERPASS_CATALOG_REQUIRED`. Google failures never trigger Overpass requests. Results are never silently merged.

19. **Languages.** New input/help/example, coverage, Maps link, uncertainty, catalog limitation, and error messages support English/Hindi/Marathi using the existing i18n lookup. Existing radius/action/source/status messages remain translated. Query values, business names, addresses, locality names, and IDs are not translated.

20. **State.** Query, radius, and loaded evidence survive language changes. Editing query/radius keeps the previous labeled result visible until a successful replacement arrives. Outstanding requests are aborted on input changes; stale responses are checked against submitted context. Proven profile-location changes clear evidence; a failed focus refresh alone no longer discards it. A result always shows its own original query/radius.

21. **Profile.** Search never writes Profile or its proposed-business selection. Suggestions do not mutate it. Existing locality/provenance behavior is retained; no location redesign was attempted.

22. **Module 15.** Catalog-driven Overpass analysis and its existing tests/rules are preserved. Free-text evidence exposes optional catalog metadata but does not force arbitrary ideas into business-model rules; the UI explains the catalog requirement for full SWOT/pricing. Because the audited Google snapshot architecture was unsafe, Google-backed saved analysis now returns controlled/localized `GOOGLE_HISTORY_UNAVAILABLE` before persisting a snapshot. Existing Module 15 tests were left unchanged and pass; the Google-specific integration test was updated to verify this explicit limitation. No Module 15 rules were rewritten.

23. **Files created in this task.**

   - `backend/app/business_query_rules.py`
   - `backend/tests/test_business_query.py`
   - `backend/scripts/run_module14_tests.py`
   - `tests/businessQuery.test.mjs`
   - `MODULE14_FREE_TEXT.md`

24. **Existing files modified in this task.** Some were already untracked before this task; this list describes edits relative to the starting workspace.

   - `backend/.env.example`
   - `backend/app/api/v1/endpoints/market.py`
   - `backend/app/core/config.py`
   - `backend/app/providers/google_places.py`
   - `backend/app/providers/nearby.py`
   - `backend/app/repositories/nearby_market_repository.py`
   - `backend/app/schemas/nearby_market.py`
   - `backend/app/services/nearby_market_service.py`
   - `backend/app/services/business_analysis_service.py`
   - `backend/tests/test_google_nearby.py`
   - `backend/tests/test_nearby_market.py` (schema-scoped introspection assertions)
   - `src/features/marketAnalysis/NearbyBusinessEvidence.tsx`
   - `src/features/marketAnalysis/nearbyState.ts`
   - `src/features/marketAnalysis/evidenceMapModel.ts`
   - `src/types/nearbyMarket.ts`
   - `src/services/marketService.ts`
   - `src/services/apiError.ts`
   - `src/i18n/runtimeMessages.ts`
   - `tests/nearbyState.test.mjs`

25. **Dependencies.** None added. Package manifests/lockfiles were already modified before this task and were not edited here.

26. **Migrations.** None needed. Transient `VALUES` queries require no new schema. Migration `20260908_10` and earlier migrations remain unchanged. The isolated test runner creates/removes only a uniquely named test schema and reuses the installed migration-09 immutability function.

27. **Frontend tests.** `npm test`: 33 passing. Covers free-text markup/optional suggestions, validation, arbitrary reducer values, all radii, locale rendering with retained snapshots/names, Google versus OSM links/source, message parity, and existing map/state/i18n regressions. These are reducer/server-render tests, not a live browser E2E run.

28. **Targeted backend tests.** 223 passing across free-text, Google provider/integration, nearby market, Overpass, and existing Module 15 service/engine tests, using mocked HTTP and real local PostGIS in an isolated schema.

29. **Full backend suite.** 438 passing. Development-cache rows initially interfered with baseline cache-count assertions; tests were then run in a disposable seeded schema. Development rows were retained. The runner requires the existing migrated PostGIS database and permission to create a temporary schema:

   ```sh
   cd backend
   .venv/bin/python scripts/run_module14_tests.py
   ```

   To run the targeted set, append:

   ```text
   tests/test_business_query.py tests/test_google_nearby.py tests/test_google_places.py tests/test_nearby_market.py tests/test_overpass.py tests/test_business_analysis.py tests/test_business_analysis_engines.py
   ```

30. **Compile.** Passed `python -m compileall backend/app` using the backend interpreter and `PYTHONPYCACHEPREFIX=/private/tmp/udyammitra-pycache`. The first attempt could not write to the environment's default cache outside the filesystem sandbox.

31. **Lint.** `npm run lint` passed.

32. **Build.** `npm run build` passed, including TypeScript and translation checks. Vite retains its large-bundle warning; no bundle restructuring was included.

33. **Whitespace.** `git diff --check` passed. Existing unrelated work was retained; no commit or deployment was performed.

34. **Known limitations.** Ranked/capped results are incomplete; circle bias can be overridden by explicit locations in user text, but PostGIS still removes out-of-radius candidates. Classification is a conservative first pass and cannot prove actual business activity. The small alias table does not cover every language/industry. Google results are fetched anew on each submission. Google history is intentionally unavailable until safe snapshots are designed; historical rows were not purged. Location remains the existing geocoded profile locality centre, not a newly verified premises coordinate. Automated tests never contacted live Google. The manual browser plan below has not been executed against live credentials.

35. **Exact manual browser steps.**

   1. Use the existing backend key without printing or changing it. Configure `NEARBY_MARKET_PROVIDER=google` locally if it is not already selected; restart FastAPI. Defaults for the new settings are sufficient, or use `GOOGLE_PLACES_TEXT_SEARCH_URL=https://places.googleapis.com/v1/places:searchText` and `GOOGLE_PLACES_TEXT_MAX_PAGES=2`.
   2. Start the existing frontend with `npm run dev`. Sign in, open Profile, and confirm saved village/taluka/district/state. Note the proposed business so it can be checked afterward.
   3. Open **Market Analysis → Real Nearby Business Evidence**. Confirm a text input appears, suggestions are optional, and an empty/one-character query cannot run.
   4. Open browser Network tools and filter to `/market/nearby`. Do not copy credentials or authorization headers into reports.
   5. Run each case below by typing the exact query, selecting its radius, and pressing **Find Nearby Businesses**:

      | Query | Radius | Inspect relevance |
      | --- | --- | --- |
      | Kirana Store | 5 km | Grocery/general/convenience establishments |
      | Tea Stall | 3 km | Tea establishments; cafes may be related |
      | Mobile Repair Shop | 5 km | Explicit repair names; retail-only stores may be related |
      | Medical Store | 2 km | Pharmacy/medical establishments |
      | Hardware Shop | 10 km | Hardware establishments |

   6. For every case, verify request `business_query`/`radius_km`, response original query, provider `GOOGLE_PLACES`, selected metre radius, and `POSTGIS_GEOGRAPHY_SPHEROID`. Every competitor/related/generic record must have `distance_meters <= selected_meters`. Confirm outside candidates are absent, list/map IDs agree, centre is shown, and exactly one selected-radius circle appears.
   7. Confirm Google Places source and coverage notice are visible. Google records must not show OSM tags or links. Open a Google Maps link and verify the requested place ID/name. Zero results should render safely with the coverage notice and centre/radius.
   8. Switch English → Hindi → Marathi after every loaded result. Query, radius, names, addresses, result counts, and map evidence must persist; only UI labels change. Edit radius/query without searching: the prior result keeps its own query/radius label. Submit again to replace it.
   9. Try `Agricultural Equipment Rental` and another arbitrary idea not in the suggestions. Confirm searching is allowed, unrelated records remain uncertain/related, and unmatched catalog metadata is null. Reopen Profile and confirm its proposed business was not changed.
   10. For error checks in a controlled test environment, use mocked timeout/4xx/5xx/malformed responses rather than damaging keys. Check localized retry messages, absence of upstream diagnostics, and no Overpass fallback.
   11. Set `NEARBY_MARKET_PROVIDER=overpass`, restart FastAPI, and select an exact catalog name from suggestions. Run at 5 km: confirm OSM source/tags/links, ordinary cache behavior, and unchanged spatial filtering. Type an unmatched arbitrary idea: confirm the controlled catalog limitation. Restore the intended provider afterward.
   12. With Overpass selected, verify existing catalog Business Analysis/Financial Plan works. With Google selected, verify saving Module 15 analysis gives the explicit live-only/history limitation rather than persisting Google display content.

36. **Coverage confirmation.** Google results are explicitly described as available/ranked nearby evidence and never as a complete business census.

37. **Distance confirmation.** PostGIS remains authoritative; no Haversine, browser distance filter, Distance Matrix, or replacement spatial calculation was introduced.

38. **Secrets confirmation and incident.** No Google API key was printed, changed, or exposed to the frontend. The initial verbose pytest connection-error traceback did expose an existing database credential. Subsequent runs use short tracebacks and avoid printing connection settings. The credential was not copied into source/docs and was not changed automatically; rotate that database credential separately.

39. **Scope confirmation.** No unrelated module was started. No AI Advisor, RAG, PDF/report-generation feature, deployment, repayment planner, financial-rule change, clustering, reviews/photos/ratings, Directions/Routes, or map redesign was added.
