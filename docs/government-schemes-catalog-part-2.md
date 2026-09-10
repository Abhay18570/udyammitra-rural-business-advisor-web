# Government Schemes Catalog — Part 2

Implemented September 10, 2026. Public read-only catalog APIs are independent of `/api/v1/schemes/analyze`. No recommendations, profile/business matching, eligibility engine, frontend or official verification workflow is implemented.

## Endpoints

| Method | Path | Response |
| --- | --- | --- |
| GET | `/api/v1/government-schemes` | Paginated active catalog |
| GET | `/api/v1/government-schemes/filters` | Distinct active filter values |
| GET | `/api/v1/government-schemes/{slug}` | Full active scheme detail |

No login is required, consistent with the existing public business catalog. There are no write endpoints. The static `/filters` route is registered before `/{slug}`. Unknown and inactive slugs both return HTTP 404 with `{"detail":"Government scheme not found."}`.

## Parameters and semantics

| Parameter | Default | Contract |
| --- | --- | --- |
| page | 1 | Integer, 1 through 2147483647 |
| page_size | 20 | Integer, 1 through 100 |
| search | absent | Maximum 200 characters; trimmed/collapsed whitespace; blank means no search |
| level | absent | CENTRAL or STATE, case-sensitive enum |
| state | absent | Maximum 100 characters; case-insensitive exact canonical state name or importer alias |
| category | absent | Maximum 200 characters; exact case-sensitive category label from `/filters` |
| verification_status | absent | DATASET_ONLY, OFFICIAL_SOURCE_LINKED, VERIFIED or STALE |
| sort | name_asc | name_asc, name_desc, newest or oldest |

Filters combine with AND. A state filter explicitly restricts to STATE schemes and never includes Central schemes. For example, `state=maharashtra` normalizes to `Maharashtra`, and `state=Orissa` to `Odisha`, using the importer's existing alias dictionary. Unknown states produce no results; no state is guessed. State and category whitespace is normalized. Category filtering uses PostgreSQL JSONB containment; use the complete label, such as `Agriculture, Rural & Environment`, not the substring `Agriculture`.

All operations enforce `is_active=true`; no query parameter enables inactive records. Metadata reflects only values present in active records, so unrepresented verification statuses are absent from metadata even though the query enum accepts all four.

Invalid pagination, enum values or oversized inputs return FastAPI's standard 422 validation response. Empty results and out-of-range pages return HTTP 200 with `items=[]`; total_pages is zero when total is zero. An out-of-range page retains the actual filtered total.

## Response contracts

`GovernmentSchemePage` contains items, total, page, page_size, total_pages and one shared disclaimer. Each `GovernmentSchemeListItem` contains:

- slug, scheme_name, short_description
- level, nullable state, categories, tags
- verification_status, source_type

The description is a whitespace-normalized prefix of details capped at 240 characters, generated in PostgreSQL. The query projects only list fields; full prose, UUIDs and search vectors are not fetched into list responses.

`GovernmentSchemeDetail` contains slug, scheme_name, details, benefits, eligibility, application_process, documents_required, level, state, categories, tags, verification_status, source_type, source_dataset, is_active, created_at, updated_at and disclaimer. Nullable application/documents fields remain null. Source prose, Unicode and currency are preserved. No official URL exists in the current model, so none is fabricated. Internal UUID and search_vector are excluded.

`GovernmentSchemeFilters` contains levels, states, categories and verification_statuses. SQL DISTINCT and ORDER BY produce sorted, duplicate-free lists; null and whitespace-only values are excluded. No huge tags list is returned.

The existing `GovernmentSchemeImport` ingestion schema remains separate from public response contracts. None of these schemas represent confirmed eligibility.

## Search, sorting and pagination

Search uses the existing stored generated English TSVECTOR covering scheme_name, details, eligibility and benefits. `websearch_to_tsquery('english', search)` is bound through SQLAlchemy, matched with `@@`, and ranked with `ts_rank_cd` descending. This is text-search relevance only, not personalized ranking.

Web-search syntax supports quoted phrases, OR and negation according to PostgreSQL semantics. English stemming and stop words apply: a stop-word-only query may return no results. There is no ILIKE fallback, fuzzy/substring search or multilingual stemming solution. The same English configuration is used for indexing and querying.

Search relevance precedes the selected sort. Name sorts use scheme_name ascending/descending. Newest/oldest use created_at descending/ascending, then scheme_name ascending. Slug ascending always breaks remaining ties, giving deterministic pagination for a stable dataset.

COUNT and projected SELECT execute in PostgreSQL with identical predicates, LIMIT and OFFSET. No full-catalog Python filtering occurs. Separate count/page statements use the project's usual transaction isolation; concurrent catalog changes can briefly produce a count/page mismatch. Offset pagination is appropriate for the current catalog size.

## Architecture and security

Endpoint → `GovernmentSchemeService` → `GovernmentSchemeRepository` → existing SQLAlchemy Session/PostgreSQL.

Repository additions are `list_schemes`, `get_scheme_by_slug` and `get_filter_metadata`. The existing importer repository method is preserved. The service normalizes read filters, assembles typed responses, handles not-found results and converts database exceptions into a sanitized HTTP 503: `Government scheme catalog is temporarily unavailable.` This also prevents debug-mode SQL exception details from leaking through these endpoints.

Query values are bound parameters, sort fields come from a fixed enum, and response fields use explicit Pydantic allowlists. No credentials or environment configuration are returned or logged. Read operations do not commit or mutate catalog data.

Every scheme response exposes its stored source_type and verification_status. Imported records remain DATASET / DATASET_ONLY; API reads do not promote statuses. List and detail responses include:

> Imported scheme information is discovery data and should be verified against current official sources before application.

The same disclaimer is included in OpenAPI descriptions. It is not stored repeatedly in database rows.

## Index and query-plan verification

No migration or index change was needed; Part 1 revision remains `20260910_12`.

Representative read-only EXPLAIN (ANALYZE, BUFFERS) queries on the actual local catalog, using API predicates, ordering and limit, returned:

| Query | Chosen index/access | Execution time |
| --- | --- | ---: |
| FTS: fisherman | Bitmap index scan, ix_government_schemes_search_vector | 1.081 ms |
| CENTRAL, name ordering | Name index scan plus incremental sort | 0.367 ms |
| Maharashtra STATE | Bitmap index scan, ix_government_schemes_state | 0.494 ms |
| Education & Learning, name ordering | Name index scan plus incremental sort | 0.231 ms |
| Slug eogu | ix_government_schemes_slug | 0.035 ms |

These are local representative query timings, not endpoint latency guarantees or production benchmarks. PostgreSQL chose the name index for broad level/category predicates with ORDER BY/LIMIT; existing level and category GIN indexes remain available. Index existence does not mean every query should use it. No observed performance gap justified new structures.

## Local validation

Actual public API totals compared directly against active PostgreSQL counts:

| Scope | API | PostgreSQL |
| --- | ---: | ---: |
| All active schemes | 3397 | 3397 |
| CENTRAL | 541 | 541 |
| STATE | 2856 | 2856 |
| Maharashtra | 80 | 80 |

Counts are verification observations, not production constants or assumptions in API tests. API tests use a small isolated PostgreSQL schema with active/inactive, Central/State and multiple verification-status fixtures.

- Targeted API + Part 1 catalog + existing Module 12 engine/endpoint suite: **131 passed** (49 new API test cases).
- Full backend suite: **580 passed, 17 failed**. The failure names match the unchanged-HEAD baseline established in Part 1: 11 business-analysis tests, 1 Google-nearby test and 5 nearby-market tests. No affected production module was changed.
- `python -m compileall backend/app`: passed, using the backend virtual environment and a writable temporary bytecode-cache directory.
- `/docs`: HTTP 200. OpenAPI exposes all three paths as GET-only, without authentication requirements, with typed response/query schemas and discovery descriptions. This verifies the Swagger backing contract, not a manual browser rendering review.
- Tests cover pagination/limits, totals, active-only behavior, all filters and combinations, four sort modes/ties, search across all indexed fields, relevance priority, empty/stop-word searches, input validation, Unicode detail fidelity, provenance, metadata ordering/deduplication, 404/503 handling, response field allowlists and rejected write methods.
- Existing Module 12 boundary tests passed without edits: ≤ ₹1.40 lakh MICRO_FINANCE; above ₹1.40 lakh through ₹50 lakh TERM_LOAN; above ₹50 lakh OUT_OF_SUPPORTED_RANGE.
- `git diff --check`: passed.

## Files and preserved work

Created in Part 2:

- `backend/app/api/v1/endpoints/government_schemes.py`
- `backend/app/services/government_scheme_service.py`
- `backend/tests/test_government_scheme_api.py`
- `docs/government-schemes-catalog-part-2.md`

Modified in Part 2:

- `backend/app/api/v1/router.py` — registers the independent catalog router.
- `backend/app/schemas/government_scheme.py` — adds public query/response schemas.
- `backend/app/repositories/government_scheme_repository.py` — adds read-only queries.

Part 1 files were already uncommitted/untracked at task start, including the model registration in `backend/app/models/__init__.py`; that prior work is preserved. Git's normal diff stat omits untracked files, including the new feature files. No Part 2 migration, model/database mutation, CSV tracking change, commit or push was made.

Financial Module modified: **NO**. Module 12 modified: **NO**. Smart Scheme Router behavior changed: **NO**. Frontend modified: **NO**.

## Known limitations and next step

Catalog content and jurisdiction remain unverified dataset hints. Category values retain source spelling/case; callers should obtain exact labels from metadata. Search is English FTS, not arbitrary substring matching. Offset pagination and separate count/page queries have the concurrency limits described above. No admin/inactive read capability, personalized recommendations or official verification workflow exists.

**Exact recommended next task:** Part 3, build the Government Schemes frontend catalog list/detail experience against these public APIs, with pagination, metadata-driven filters, search and the shared discovery disclaimer. Keep the existing financing pathway and Module 12 UI/behavior intact; do not add personalized recommendations without a separate task.
