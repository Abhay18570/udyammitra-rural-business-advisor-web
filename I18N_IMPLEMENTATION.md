UdyamMitra multilingual continuation — 8 September 2026

The existing working tree was continued without reverting earlier work. Its initial status/diff included substantial pre-existing Google Maps, Google Places, financial, profile and Module 15 work. Those backend changes and migrations were preserved; this localization continuation did not modify backend files, environment files, calculations, database enums or migrations. No dependencies or translation framework were installed.

Partial-work audit

The original custom UiProvider, English/Hindi/Marathi dictionaries, public language selector and some public/market/scheme translations already existed. Authenticated navigation, forms, status labels, error messages and feature pages had incomplete coverage. Local storage existed, but authenticated preference integration and website-wide display boundaries needed completion. During continuation, malformed JSX from bulk label wrapping, translated React keys, encoded entities inside string props and a locale-dependent nearby-market loading effect were found and corrected. The final checks below describe the resulting tree, not the initial state.

Implementation and architecture

The same UiContext provides language, setLanguage, the existing t object, text() and date(). LocalizedText is an explicit React display component; it does not scan or mutate the DOM. English remains the canonical source text. Existing nested keys remain intact. Additional messages are grouped by feature and resolved by canonical English text; backend messages can use numbered interpolation placeholders. Central status labels convert identifiers only at display time. Unexpected messages remain readable through a safe original-text fallback.

All 1,520 catalog entries have nonempty English, Hindi and Marathi values with matching numbered placeholders: 146 original nested keys, 807 general messages, 509 runtime/catalog messages and 58 enum/status entries. This counts catalog entries, including compatible aliases, rather than unique English phrases. Existing keys were retained to avoid needless churn. Build-time tests reject missing locale keys, missing placeholders and untranslated literal LocalizedText labels other than the explicit proper-name allowlist.

Preference behavior

There is one presentation language state. Public choices persist under udyammitra-language in localStorage; unsupported values or unavailable storage fall back safely to English. The selector shows English, हिन्दी and मराठी. Authenticated saved preferences initialize through the existing user/profile data. Explicit choices win over delayed profile responses, and writes are serialized. A pre-login explicit selection carries through login and is saved to the account. Failed saves retain the local choice and show a translated retry notice. Saves use the existing /profile endpoint with preferred_language and the required current onboarding_step; they do not send unrelated form or analysis values. No update runs merely because a page renders.

State and formatting

Language changes update context without navigation or locale-based component keys. Analysis loaders do not depend on language or translated labels. In particular, the nearby loader no longer refetches and resets its selected business when the error label changes language. Onboarding submission uses the current presentation preference. Dates use en-IN/hi-IN/mr-IN with Latin digits; currency keeps the existing exact Indian grouping helper, including ₹1,40,000 and ₹50,00,000. Names, IDs, amounts and stored enums remain unchanged.

Coverage

| Area | Display coverage |
| --- | --- |
| Navigation and shared UI | Dashboard, sidebar, public/mobile navigation, buttons, breadcrumbs, notices, placeholders, accessibility labels |
| Public/auth | Landing, login, registration, password recovery, labels, placeholders, validation and notices |
| Onboarding | Six-step headings, guidance, option labels, progress, errors, actions and preferred-language control |
| Profile | Sections, financial/location labels, known skills/resources, missing values and edit actions; user-entered names remain raw |
| Market Analysis | Selectors, radius, summary, status, coverage warnings, provider labels, map legend, marker titles and text evidence |
| Business Opportunities | Scores, factors, skill/resource lists, catalog descriptions, capital explanations, strengths, gaps, risks and next steps |
| Financial Plan | Inputs, calculations display, cost ranges, funding gaps, financing guidance and saved-state notices |
| Government schemes | Eligibility, financing limits, contribution/gap guidance, terms and next actions; official scheme names retained |
| Business Analysis | Overview, SWOT, threats, mitigation, mapped competition, pricing availability, evidence and data-quality labels |
| Other routes | Existing Documents, AI Advisor, My Analyses, Reports, Settings and administration placeholders; no missing feature was implemented |

Known backend error codes are mapped in the frontend API error layer, then localized at display time. Known English detail strings and runtime explanation templates also have frontend translations. Unknown responses retain their original text. Zod/schema logic is shared across languages; display-time translation relabels validation messages, including errors already visible when language changes.

User-facing aria-label/title/alt text uses the display helper where owned by the application. Map provider names and attribution remain intact. Hindi/Marathi styles give labels and controls more line height and safe word wrapping, using installed Devanagari/system font fallbacks without adding font files. No UI redesign was performed.

Intentionally retained text

- User-entered names, addresses, free-text Other descriptions and business names.
- External Google/OSM business/place names and provider attribution.
- Canonical business catalog titles, including Kirana / General Store and Mobile Repair & Accessories, retain their identity across screens. Their descriptions and guidance translate.
- Official government scheme names, UdyamMitra and external provider/service names.
- Evidence IDs, rule versions, context hashes, raw evidence JSON, provider tags and other original technical provenance inside evidence disclosures.
- Unknown future API text safely falls back to the supplied text. New known messages should be added to the catalogs.

Validation

- Targeted i18n tests: 15 passed.
- Full frontend suite: 29 passed, including existing nearby-state and mocked map tests.
- Coverage includes all three locale renders, feature labels, key/placeholder parity and missing-key rejection, stored language, authenticated-save payload, delayed preference guards, enum/validation/error display, currency/date formatting, literal label audit, proper-name preservation and immutable map/profile snapshots.
- Structural regression tests reject locale dependencies or locale keys in onboarding and market/financial/scheme/business-analysis loaders. These are not a substitute for interactive browser tests.
- npm run lint: passed without warnings.
- npm run build: passed; Vite reports the large bundle warning.
- git diff --check: passed.
- No test calls live Google or OSM APIs. Backend tests were not run because this continuation did not change backend code.

Remaining verification limits

No browser automation tool is available in this session. Interactive route switching, form/analysis state preservation, login/logout behavior against a running backend and responsive glyph rendering have not been exercised in a browser. SSR, pure-helper, mocked-service and structural checks passed; they do not establish those browser outcomes. Native-speaker review of the Hindi/Marathi copy is also recommended. Raw provenance JSON and unexpected backend messages can contain English by design. Catalog parity does not prove coverage of every possible future backend response.

Exact manual browser verification

1. Run the project's backend using its existing local setup, then run npm run dev. Open the URL printed by Vite. Open browser Network tools and enable Preserve log. Do not share or print environment keys.
2. Select English in the public header. Visit /, /login, /register and /forgot-password. Submit empty/invalid forms; check labels, errors and password visibility controls. Refresh and confirm English remains selected.
3. Log in with a test account. Open /dashboard. Check sidebar labels, collapse/expand, mobile menu and header selector. Open /onboarding?mode=edit, visit all six steps, and check labels/options, Back, Save & Continue and Finish. Enter test values without submitting unwanted profile changes.
4. Open /profile and confirm names/locations match the stored input exactly. Open /market-analysis, choose a supported business/radius and run one analysis. Record the business, radius, result ID/counts and visible map names.
5. While that result is visible, select हिन्दी, then मराठी, then English. Confirm route, business, radius, result ID/counts and names remain unchanged, with no new market request. Expand text evidence and check its labels, source, distance and freshness.
6. Open /opportunities and a detail link. Check descriptions, factor labels, skill/resource lists, risks, capital fit and actions in each language. Canonical business titles should remain identical.
7. Open /financial-plan and choose a business. Enter own capital and requested loan, calculate once, and note input values/result amounts. Change language without leaving the route. Confirm values/results remain and no financial recalculation request occurs. Check Indian grouping and translated range/gap guidance.
8. In the Financial Plan scheme panel, check eligibility once. Change language and verify the same scheme result remains; official scheme names and numbers stay unchanged, with no extra scheme request.
9. Open /business-analysis from its existing financial-result action. Load/run one result, note the result ID, and expand SWOT, threats, competition, pricing and evidence. Change languages and confirm the same result remains without another analysis request. Check severity, mitigation, unavailable-data wording and dates.
10. Visit /documents, /advisor, /my-analyses, /reports and /settings. Check each existing heading/placeholder and navigation in all three languages. No new feature should appear.
11. Repeat steps 3–10 with हिन्दी selected at the start, then again with मराठी selected at the start. Trigger validation in every onboarding step; errors already visible should change language immediately. Check that manually entered text remains unchanged.
12. Select Marathi while logged in. Wait for the preference request to finish, refresh, log out and log back in without making another explicit language choice; verify the saved preference loads. Repeat with Hindi and English. For a separate pre-login test, explicitly choose another language on the login screen and confirm that choice wins during login and is saved.
13. Repeat key routes at 375px, 768px and desktop width. Open the mobile menu, expand sidebar labels, inspect long buttons/table headers and scroll evidence cards. Confirm Hindi/Marathi vowel marks are not clipped and content does not cause unintended horizontal overflow.
14. Disable optional storage in a disposable browser profile and confirm the app still renders. Simulate a failed profile save using browser request blocking; confirm the local language changes, the translated save notice appears and selecting the language again retries.

Localization file inventory

New localization/support files: src/i18n/LocalizedText.tsx, src/i18n/localize.ts, src/i18n/messages.ts, src/i18n/runtimeMessages.ts, src/i18n/statusMessages.ts, tests/i18n.test.mjs, tests/tsxLoader.mjs and I18N_IMPLEMENTATION.md. Existing tests/evidenceMap.test.mjs was adapted to the shared language context and extended. Earlier untracked feature/provider files remain untracked; their presence does not mean this task created those features.

Existing integration/configuration files changed for localization: package.json, src/App.tsx, src/i18n/I18nContext.tsx, src/i18n/translations.ts, src/i18n/uiContextValue.ts, src/services/profileService.ts, src/services/apiError.ts and src/responsive.css. No dependency installation was needed.

Frontend display consumers containing the localization boundaries (some had partial translations before continuation):

- src/components/auth/AuthFields.tsx
- src/components/auth/AuthNotice.tsx
- src/components/common/Brand.tsx
- src/components/landing/LandingHero.tsx
- src/components/landing/LandingSections.tsx
- src/components/layout/Footer.tsx
- src/components/layout/LanguageSelector.tsx
- src/components/layout/PublicHeader.tsx
- src/components/ui/Card.tsx
- src/components/ui/Feedback.tsx
- src/components/ui/FormControls.tsx
- src/components/ui/Navigation.tsx
- src/features/businessAnalysis/BusinessAnalysisPage.tsx
- src/features/businessCatalog/BusinessCatalogPage.tsx
- src/features/businessCatalog/BusinessDetailPage.tsx
- src/features/businessCatalog/FeasibilityViews.tsx
- src/features/dashboard/DashboardHeader.tsx
- src/features/dashboard/DashboardPage.tsx
- src/features/dashboard/DashboardPanels.tsx
- src/features/dashboard/JourneyProgress.tsx
- src/features/dashboard/ProfileSnapshot.tsx
- src/features/dashboard/QuickActions.tsx
- src/features/financial/FinancialPlanPage.tsx
- src/features/financial/SchemeEligibilityPanel.tsx
- src/features/marketAnalysis/MarketAnalysisPage.tsx
- src/features/marketAnalysis/MarketMap.tsx
- src/features/marketAnalysis/NearbyBusinessEvidence.tsx
- src/features/onboarding/OnboardingPage.tsx
- src/layouts/AdminLayout.tsx
- src/layouts/AuthLayout.tsx
- src/layouts/UserDashboardLayout.tsx
- src/pages/PlaceholderPage.tsx
- src/pages/auth/ForgotPasswordPage.tsx
- src/pages/auth/LoginPage.tsx
- src/pages/auth/RegisterPage.tsx
- src/pages/public/HomePage.tsx
- src/pages/user/ProfilePage.tsx
- src/routes/AppRouter.tsx
- src/routes/ProtectedRoute.tsx
