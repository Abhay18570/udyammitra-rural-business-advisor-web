# Government Schemes Catalog — Part 3

Implemented September 11, 2026. Scope: frontend catalog integration only. Parts 1 and 2 were already uncommitted in the workspace and remain preserved.

## Routes and financing separation

- `/government-schemes`: public catalog page.
- `/government-schemes/:slug`: public, read-only detail page.
- `/schemes`: existing authenticated workspace entry now composes the same catalog page inside its existing dashboard layout.
- Public header and footer Government Schemes links point to `/government-schemes`. Existing authenticated workspace links remain valid.

The page has a Government Schemes header, **Your Financing Pathway**, then **Explore Government Schemes**. For signed-in USER accounts the pathway renders the original `features/schemes/GovernmentSchemesPage` component without changing its source, service, calculations, rule constants or saved-context handling. The enclosing section supplies the new heading; scoped CSS hides only the old redundant page header. Its original guidance source, profile illustration fallback, Micro Finance/Term Loan terms, comparisons and result cards remain intact.

Public visitors see a sign-in link for personal financing guidance and can browse the entire catalog without authentication. Catalog dataset records never enter the financing component and never display Eligible, Approved or Recommended badges.

## API integration and types

`governmentSchemeService` reuses the existing Axios `apiClient` and token handling:

- `list(query, signal)` → GET `/government-schemes`
- `filters(signal)` → GET `/government-schemes/filters`
- `detail(slug, signal)` → GET `/government-schemes/{encoded-slug}`

TypeScript contracts mirror backend snake_case names: `GovernmentSchemeListItem`, `GovernmentSchemeListResponse`, `GovernmentSchemeDetail`, `GovernmentSchemeFilters`, `GovernmentSchemeQuery`, plus controlled level/status/sort unions. No `any`, new fetch stack, runtime translation service or application dependency was introduced.

The request hook cancels obsolete requests and ignores aborted responses. Request-keyed state prevents old results from being displayed under new filters. Metadata loads independently of the list; catalog filtering does not refetch financing guidance. Detail data loads only on its route. React StrictMode may start and immediately cancel a development-only initial effect, consistent with React behavior.

## Catalog behavior

- Search uses a 400 ms debounce, backend English full-text search and a 200-character bound.
- Search, level, state, category, verification status and sort changes reset page to 1.
- Level/state/category/status options come from `/filters`. Labels for enums are translated; actual state/category values remain source values.
- Selecting CENTRAL clears and disables state. A shared URL with CENTRAL and state also omits state from the API request.
- Sort values are name_asc, name_desc, newest and oldest. A visible note explains that search relevance precedes selected sort.
- Backend pagination uses 20 items per page, Previous/Next controls and filtered total/page indicators. No full catalog is downloaded into the browser.
- URL query parameters preserve filtering, sorting and page on refresh, detail navigation and browser Back/Forward. The detail link carries the catalog query, and Back to catalog restores it. Search input remounts on query navigation to prevent an old draft search from replaying after Back.
- Clear filters resets the query and any pending draft input. Invalid URL enum/page values are normalized to safe defaults.

Cards show name, Central/State badge, known state, two category badges plus +N more, lightweight preview, verification/source badges and View Scheme. Tags and full eligibility/benefit/application/document prose are omitted from list cards.

## Detail and provenance

Detail renders source overview, benefits, eligibility, application process, documents, level, state, all categories/tags and source/verification. Null prose displays a translated unavailable message. React renders source text as text; line breaks are preserved with `white-space: pre-wrap`. There is no HTML injection or automatic eligibility interpretation.

Verification uses text plus color: Dataset Only amber, Official Source Linked blue, Verified green and Stale warning amber/red. Dataset provenance has a separate neutral badge. Public list and detail display a translated discovery disclaimer; future VERIFIED records use a status-appropriate current-terms reminder.

The current backend contract has no official/application URL field. The detail page says **Official source link not available in this dataset.** No official URL or Apply Now action is fabricated, and URLs embedded in prose are not automatically promoted to authoritative links. The View Official Source UI phrase is translated for future use, but no unsupported URL field is invented.

## Loading, errors, accessibility and responsive layout

Filter metadata, list and detail have semantic status skeletons. Empty search results have a clear message and filter-reset action. Metadata/list/detail errors use friendly translated messages with retry buttons, without displaying raw API diagnostics. Missing/inactive detail returns a friendly not-found heading.

Search and selects have localized accessible names; cards use article/headings, links have scheme-specific accessible names, pagination has a named nav and disabled boundary controls. Focus outlines remain visible, and status distinctions do not depend on color alone. Desktop has three card columns, tablet two, mobile one; filters collapse to a single column. Long names/prose wrap and pagination wraps.

EN/HI/MR chrome is integrated through the existing `useUi().text` system and a catalog message group registered with `localize.ts`. Scheme names, imported prose, state/category/tag values and dataset filenames are not runtime-translated.

## Verification

### Automated frontend checks

- `npm test`: **161 passed**, including **19 new catalog tests** and the existing financing tests.
- `npm run lint`: **passed with no warnings**.
- `npm run build`: **passed**, including i18n checks and TypeScript. Vite retains its large-chunk advisory; no heavy runtime dependency was added.
- `git diff --check`: passed.

New Node tests cover page/pathway composition, service endpoints and cancellation signals, cards/provenance, Central/State display, complete detail prose, unavailable official links, loading/error semantics, all three languages, query persistence/reset, input normalization and debounce timing/cancellation. Existing financing tests continue to cover original result rendering, boundaries and financial formatting.

### Real Chromium checks

`tests/governmentSchemes.browser.mjs` is an optional reproducible browser runner. Playwright/Chromium were installed only under a temporary directory, not in the project or lockfile. Run with local frontend/backend servers and an available Playwright module:

```sh
PLAYWRIGHT_MODULE=/path/to/playwright/index.mjs \
PLAYWRIGHT_BROWSERS_PATH=/path/to/browser-cache \
node tests/governmentSchemes.browser.mjs
```

The runner defaults to frontend `http://127.0.0.1:5173` and API `http://127.0.0.1:8000/api/v1`; override CATALOG_WEB_ORIGIN/CATALOG_API_ORIGIN if needed. It uses real catalog responses. Only loading/error cases and saved user/financing context are controlled browser mocks; no database user or financial records are created.

Passed checks:

- Public page, real API total **3397**, 20 rendered cards.
- Search **dairy: 65** results; one completed debounced search request after typing.
- STATE + Maharashtra: **80** records; displayed scheme names agree with actual API responses.
- Level/category/verification/sort interactions, page 2, CENTRAL state reset/disable.
- Detail open, exact overview/benefits/eligibility parity, no Apply Now or invented official source.
- Browser Back, refresh and query persistence, including Back after typing a search.
- Loading/error/empty states with controlled response delays/failures; no raw error marker shown.
- Hindi and Marathi UI after language persistence/reload.
- 1440px/768px/390px viewport layouts: 3/2/1 columns, no horizontal document overflow. Desktop/mobile screenshots were inspected.
- Signed-in `/schemes` renders the original saved-context Micro Finance and Term Loan results using controlled guidance responses; the separate real catalog remains free of eligibility claims.
- No page JavaScript exceptions.

The opened `fatnukyv` detail was additionally compared read-only against PostgreSQL: scheme name, overview, benefits, eligibility, application, documents, state, categories and tags all matched. Catalog counts are observations, never hardcoded production constants.

## Files

Created:

- `src/types/governmentScheme.ts`
- `src/services/governmentSchemeService.ts`
- `src/i18n/governmentSchemeMessages.ts`
- `src/features/governmentSchemes/GovernmentSchemeCatalogPage.tsx`
- `src/features/governmentSchemes/GovernmentSchemeDetailPage.tsx`
- `src/features/governmentSchemes/CatalogViews.tsx`
- `src/features/governmentSchemes/catalogLabels.ts`
- `src/features/governmentSchemes/catalogState.ts`
- `src/features/governmentSchemes/useCatalogRequest.ts`
- `src/features/governmentSchemes/catalog.css`
- `tests/governmentSchemes.test.mjs`
- `tests/governmentSchemes.browser.mjs`
- `docs/government-schemes-catalog-part-3.md`

Modified in this phase:

- `src/routes/AppRouter.tsx`: public list/detail and existing workspace composition.
- `src/main.tsx`: catalog stylesheet registration.
- `src/i18n/localize.ts`: catalog message registration.
- `src/components/layout/PublicHeader.tsx`: public catalog navigation target.
- `src/components/layout/Footer.tsx`: public catalog navigation target.

No backend file, migration, importer, credential, package manifest or lockfile was changed in Part 3. Prior backend changes visible in git status belong to Parts 1/2. No commit or push was performed.

Financial Module modified: **NO**. Module 12 business rules modified: **NO**. Smart Scheme Router behavior changed: **NO**. Backend modified in Part 3: **NO**.

## Known limitations and exact next step

The imported content and geographic hints remain discovery data, not verified eligibility. Search is backend English FTS; dataset prose and category names retain their source language/spelling. Official source fields do not yet exist. Requests use the project's simple effect/service pattern without persistent caching. The existing financing section remains extensive because its original content is preserved. Bundle-size optimization remains separate work.

**Recommended next task:** design a separately authorized personalized-discovery matching specification, starting with reliable inputs, data-quality/jurisdiction review, provenance safeguards and evaluation cases. Do not present matches as confirmed eligibility or change Module 12. No recommendation implementation has been started here.
