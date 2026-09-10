# Administration — Part 2

Part 2 adds real geographic analytics and a read-only entrepreneur list. It preserves bootstrap behavior, Part 1 authorization, and the entrepreneur dashboard. Business, financial, scheme, and analysis analytics remain outside this change.

## Audit and architecture

The existing admin router already enforces `require_admin`, which resolves the active account and current database role using the existing authentication dependency. The profile has a unique indexed user_id, indexed proposed_business_id, nullable state/district/taluka/village fields, a nullable has_existing_business flag, and onboarding_completed. User supplies the real name, email, mobile, language, and registration timestamp. The existing business catalog supplies proposed-business names.

The repository selects columns rather than loading profile ORM objects and their skills/resources relationships. State and district statistics use PostgreSQL GROUP BY, COUNT, DISTINCT and aggregate summaries. Only aggregated location rows enter Python; percentages use Decimal with ROUND_HALF_UP to two decimal places. The list uses COUNT plus LIMIT/OFFSET with backend filters and deterministic timestamp/ID ordering. No SQL or totals are calculated in React.

Recharts was already installed. Geographic pages and the chart bundle load on demand. Tables use semantic headers and horizontal scrolling, following the existing table approach without adding a component dependency.

## Routes and API contracts

| Browser route | Purpose |
| --- | --- |
| /admin/analytics/geography | State summary, bar chart, table |
| /admin/analytics/geography/state/:stateKey | Selected state summary, district chart, table |
| /admin/entrepreneurs | Searchable, filtered, paginated USER account list |

All routes are nested under the existing admin guard and AdminDashboardLayout. The sidebar now links to Entrepreneurs and Geographic Analytics. The Part 1 dashboard adds a single geographic analytics link.

| API | Contract |
| --- | --- |
| GET /api/v1/admin/analytics/states | total_entrepreneurs, located_entrepreneurs, missing_state_count, states_count, districts_count, states |
| GET /api/v1/admin/analytics/states/{state}/districts | state, state_key, total_entrepreneurs, districts_count, missing_district_count, new_enterprises, existing_enterprises, districts |
| GET /api/v1/admin/entrepreneurs | items, total, page, page_size, total_pages |

A state row includes state, state_key, entrepreneur_count, percentage, districts_count, new_enterprises, existing_enterprises. A district row includes district, district_key, entrepreneur_count, percentage, new_enterprises, existing_enterprises. Counts are integers and percentages are decimal strings.

## Location semantics and drill-down

Comparison keys reuse Part 1's PostgreSQL whitespace collapse, trimming, lowercasing and blank-to-null normalization. No abbreviation or geocoding mappings are invented. Display names are deterministic representatives from saved profile text with whitespace cleaned; proper nouns are never passed through translation. Database values are not rewritten.

State percentages use profiled USER accounts with a nonblank state as the denominator. District percentages use profiled USER accounts in the selected state with a nonblank district. Percentages are independently rounded and may sum to 99.99 or 100.01. Missing locations are reported separately and are not fictitious chart bars. Null enterprise status contributes to neither new nor existing.

State bar clicks and View Districts links encode the normalized state key in the route. District clicks and View Entrepreneurs links use URLSearchParams for state/district filters. The API matches normalized locations through bound SQLAlchemy expressions. Unknown states return 404. State names containing slashes are supported by the backend path route.

Geography cards use the state response, with no extra overview request. State details show the state's total, district count and new/existing breakdown. Charts use API counts and percentages in tooltips. Full table equivalents provide navigation without chart clicking.

## Entrepreneur list

The source is USER accounts left-joined to their profile and proposed business. ADMIN and SUPER_ADMIN never appear. Without location filters, pending accounts can appear. With state/district filters, only matching profiles appear.

Supported parameters:

- page: default 1, range 1–1,000,000.
- page_size: default 20, range 1–100; UI offers 20, 50 and 100.
- search: up to 160 characters, case-insensitive literal substring of full name, email, mobile, village, district, state or proposed-business name. LIKE wildcard characters are escaped. This is a literal search; internal whitespace is not normalized like exact location filters.
- state/district: normalized exact matches, up to 100 characters.
- enterprise_status: new, existing, unspecified.
- sort: created_desc (default) or created_asc; a stable internal ID breaks ties but is not returned.
- business_slug: optional API filter; no business analytics or UI filter is added.

Filters populate from the URL and remain visible when arriving from a district. State/district inputs are explicit text filters, avoiding extra metadata requests. Apply resets page to 1; Clear Filters removes all filters. Pagination preserves filters. Total_pages is zero for no results, with the UI displaying Page 1 of 1 and disabled navigation on the default empty page.

Returned operational fields: full_name, email, mobile_number, state, district, taluka, village, enterprise_status, proposed_business, preferred_language, created_at, profile_status. No internal relation IDs, password hashes, tokens, credentials or provider data are returned. List responses set Cache-Control: no-store.

Profile status is pending for no profile, complete for onboarding_completed=true, otherwise created. Enterprise status comes exclusively from has_existing_business; null/no profile is unspecified. Missing proposed business/location is displayed as Not Provided. No completion percentage is invented.

## UI, accessibility and privacy

The existing EN/HI/MR lookup translates UI labels, instructions, status values and errors. Proper names and entrepreneur text retain their saved values. Summary cards stack on narrow screens. Long chart labels wrap without truncation, and chart/table containers can scroll horizontally with keyboard focus. Semantic tables, captions, explicit filter labels, visible focus styles, accessible loading regions and error alerts are provided.

Loading uses skeleton summaries, chart areas and table areas without fake zeros. Separate empty messages handle no state data, missing states, missing districts and unmatched list filters. API errors show safe fixed messages with retry; 403 shows the permission message and 401 clears the session and returns to login. AbortController and request-path checks prevent stale responses from replacing a new filtered view.

The geographic pages remain aggregate-only. Personal fields appear only on explicit navigation to the protected entrepreneur list. No entrepreneur details, editing, deletion, impersonation, exports or maps are implemented.

## Index assessment

The existing unique profile user_id index supports the join; proposed_business_id is indexed. Models have no dedicated users.role or normalized state/district indexes. No migration is justified by the tiny current development dataset. Before production, inspect EXPLAIN (ANALYZE, BUFFERS) at realistic scale and evaluate an expression index on the exact normalized state/district expressions, and an index supporting role plus registration ordering. Plain raw-location indexes would not directly cover these normalized predicates. Materialized views are unnecessary at this stage.

## Verification and manual acceptance

Automated backend coverage includes all three APIs across unauthenticated/USER/ADMIN/SUPER_ADMIN roles, normalized grouping, missing states/districts, cross-state district names, percentages, new/existing counts, zero profiles, unknown state, encoded state names, list pagination, limits, filters, literal search, timestamp sorting, pending/completed profiles, business join, and the response field allowlist.

Frontend coverage includes single-state data, chart/table values, click callbacks, encoded destinations, query-populated filters, apply/clear/pagination handlers, service paths, empty/loading/error states, translations, access guards, scroll structure and request cancellation wiring. These component/static-render checks do not substitute for interactive browser acceptance.

Manual browser steps:

1. Start the existing backend and frontend; sign in with the configured administrator account.
2. Open /admin/analytics/geography. Compare summary counts with PostgreSQL; chart and state table must agree.
3. Click a state bar or View Districts. Check real district totals, missing-location notice if applicable, and shares.
4. Click a district or View Entrepreneurs. Confirm state and district are visible in filters and only matching rows appear.
5. Apply search, enterprise status and sort; test page size and Previous/Next. Clear Filters and verify pending accounts can appear.
6. Switch EN/HI/MR; verify proper names remain unchanged. Resize to mobile, use the menu and keyboard-scroll charts/tables.
7. Log out and sign in as an entrepreneur. Both geography and entrepreneur list routes must redirect to the user dashboard. All three admin APIs must return 403 for that USER.

No browser automation runtime is available in this workspace, so interactive browser testing is outstanding. Local API login and PostgreSQL cross-checks were performed without printing credentials or entrepreneur details.

## File inventory

Created:

- backend/tests/test_admin_geography.py
- src/features/admin/AdminData.tsx
- src/features/admin/useAdminData.ts
- src/features/admin/GeographyChart.tsx
- src/features/admin/GeographicAnalyticsPage.tsx
- src/features/admin/StateAnalyticsPage.tsx
- src/features/admin/EntrepreneursPage.tsx
- src/features/admin/entrepreneurFilters.ts
- tests/adminGeography.test.mjs
- docs/admin-part-2.md

Extended from Part 1:

- backend/app/api/v1/endpoints/admin.py
- backend/app/repositories/admin_repository.py
- backend/app/services/admin_service.py
- backend/app/schemas/admin.py
- src/services/adminService.ts
- src/layouts/AdminDashboardLayout.tsx
- src/features/admin/AdminDashboardPage.tsx
- src/features/admin/admin.css
- src/routes/AppRouter.tsx
- src/i18n/messages.ts

No dependencies, migrations, bootstrap changes or entrepreneur layout/navigation changes. Earlier uncommitted work was preserved.

## Final validation results

- Targeted Part 1 + Part 2 admin backend tests: 52 passed, including 44 new Part 2 cases.
- Full backend suite: 486 passed, 17 failed. The failure names match the unchanged-HEAD baseline established in Part 1; failures remain in business analysis, Google nearby and nearby market tests.
- Frontend suite: 117 passed, including 15 new geography/list tests.
- Python compileall, frontend lint, production build and git diff --check: passed. Python used a writable temporary cache directory.
- The build emits separate geographic page/chart chunks. The pre-existing large main-bundle warning remains.
- Local ADMIN authentication and all state/district/list reads succeeded. Independent PostgreSQL grouping matched 6 profiles, 1 represented state and 6 district pairs; all 6 district-filtered lists matched their counts. These values are observations, not application constants.
- An existing active USER received 403 on all three new APIs. Test accounts also verified ADMIN/SUPER_ADMIN 200 and unauthenticated 401 behavior.
- Interactive browser verification remains outstanding; follow the manual steps above.
