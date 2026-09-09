# Google Maps migration verification

Scope: frontend visualization only. Existing backend logic and API contracts are unchanged. All three map consumers (real Market Analysis, saved Business Analysis, and demonstration analysis) use `EvidenceMap` in `MarketMap.tsx`. `evidenceMapModel.ts` adapts normalized POIs; `googleMapArea.ts` creates a single radius circle and extends its bounds with the returned marker positions. There are no discovery requests in these modules.

## Manual browser checks

1. Start your existing configured database and backend. In one terminal run `cd backend`, `source .venv/bin/activate`, then `uvicorn app.main:app --reload`. Keep your existing backend `.env`.
2. From the repository root in a second terminal run `npm run dev`. Use the URL Vite prints. Keep your existing frontend `.env` with `VITE_GOOGLE_MAPS_API_KEY` configured.
3. Sign in with an onboarded profile with a valid locality and proposed business. Open `/market-analysis`.
4. Confirm the proposed business is selected and radius defaults to 5 km. Click **Find Nearby Businesses**. In browser Network tools inspect the `/api/v1/market/nearby` response.
5. Confirm Google Maps loads, the blue **C** centre matches `location.latitude/longitude`, and exactly one circle represents `radius.selected_meters` (5000).
6. Compare red **D** markers to `competitors` and amber **R** markers to `related_businesses`. Click each role: verify name, classification, backend distance and OpenStreetMap/Overpass source. Confirm the centre popup names the resolved locality.
7. Compare displayed counts and nearest competitor with `summary`. Verify source/freshness and coverage warnings still appear. Confirm Google is labeled as visualization, OpenStreetMap/Overpass as evidence, and PostGIS as distance calculation.
8. Change radius to 1 km: old evidence must disappear immediately without another request. Click **Find Nearby Businesses**; verify one 1000-meter circle and a closer camera. Repeat with 10 km and one 10000-meter circle with a wider view.
9. Change the business: old evidence must clear without searching automatically. Run a new explicit search.
10. Collapse/expand the sidebar repeatedly, resize the browser, and check tablet/mobile widths. Verify the canvas fills its panel with no horizontal overflow. Pan/zoom manually: ordinary rerenders and sidebar changes should preserve the camera. Open the demo disclosure and confirm its Google map fits when first visible and retains demo labels.
11. Use a locality/business response with zero mapped direct competitors. Confirm the centre and selected circle remain visible, related markers remain if present, and wording says “No mapped direct competitors” rather than asserting no competitors exist.
12. Open `/business-analysis` with a valid saved analysis. Compare SWOT, threats, competition, density, nearest competitor, pricing/unavailable states, evidence references and quality warnings with the saved response. Confirm marker counts and radius agree with `market_context`.
13. Clear the Network log and reload the saved analysis. A saved-analysis retrieval and Google map asset requests are expected; map loading must not trigger `/market/nearby`, public Overpass discovery, or Google Places/Geocoding requests.
14. Check keyboard navigation to map controls/markers and opening/closing info windows. Expand the text evidence list and confirm names, classifications, distances and sources can be read without using the map. Legend letters/text identify roles independently of color.
15. Stop the frontend. In a fresh terminal at the root run `VITE_GOOGLE_MAPS_API_KEY= npm run dev`. This overrides the key for that process without editing `.env`. Repeat both analysis pages: the map says “Google Maps is not configured for this environment.” Counts and evidence lists remain usable. Stop this process and restart normally afterward.
16. With a configured key, block `maps.googleapis.com` using browser request blocking and reload. Verify a local loading failure/timeout message and usable analysis content. Disable blocking afterward. An invalid/restricted key should also show the map failure message; do not capture keys in screenshots or reports.

## Validation and limitations

Automated tests use mocked Google components and circle geometry, checking missing-key/load/auth fallbacks, centre/marker rendering, safe POI text, exact radius transfer, zero evidence, consumer wiring and existing state transitions. They do not validate live tiles, Google billing/referrer configuration, actual keyboard focus, sidebar animation rendering, or saved backend responses. The browser checklist above remains required for those checks.

Advanced markers use `DEMO_MAP_ID` (a public Google demonstration map identifier, not an API key). The APIProvider manages the shared script load; there are no manual script tags. Camera fitting occurs only for changed evidence geometry or first visibility; later container resizing preserves the camera. Closely overlapping markers may overlap visually; the text list retains every record. Existing English map labels are retained; map-specific label translation is not part of this migration.

Production build retains the existing Vite warning for a JavaScript chunk above 500 kB. No unrelated bundle optimization or next-module work was performed.
