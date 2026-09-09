# UdyamMitra landing-page redesign

Implemented only the public home experience. Existing uncommitted backend, dashboard, map, financial, scheme and localization work was present before this task and was retained.

## Audit and scope

- Inspected `git status`, `git diff --stat`, `git diff`, the active `/` route, public layout/header/footer, legacy `LandingHero`/`LandingSections`, UI provider, translation catalogs, route definitions, shared branding, loading/accessibility utilities, Lucide icons, CSS tokens/responsive styles and static assets. No applicable AGENTS.md was found.
- `/` rendered a large inline `HomePage`: split text/journey hero, update strip, six service cards, process/evidence sections, business examples, financial/scheme cards, language strip, transparency and final CTA. Legacy `LandingHero` was not mounted; it remains untouched.
- The old page labelled implemented Financial Planning as upcoming and used `/financial-plan/preview`. The new links use `/financial-plan`.
- `/market-analysis`, `/opportunities`, `/financial-plan`, `/business-analysis` and `/schemes` exist behind the existing authentication guard. `/advisor` and `/documents` are placeholder routes. No router/authentication logic was changed.
- No reference screenshot files were available in this task; the supplied written visual brief guided the original design.

## Final UI and behavior

| Requested area | Implementation |
| --- | --- |
| Page structure | Utility bar → sticky navigation → full-width carousel → Quick Access → four help features → Explore UdyamMitra → six-step journey → scheme summaries → transparency strip → footer. |
| Utility/header | Existing India identity, runtime language selector, skip link and A−/A/A+ controls retained. Home adds an accessibility anchor and clear SIH prototype wording. |
| Navigation | Home, How It Works anchor, Opportunities, Market Analysis, Schemes, AI Advisor, Login and Get Started. Home is active; the mobile disclosure supports Escape, close button and backdrop. |
| CTA routing | Get Started opens `/register` when logged out and `/dashboard` when authenticated. Existing protected service routes continue through the current login guard. |
| Carousel architecture | `HeroCarousel`, `HeroSlide`, `CarouselControls`, a small state/scheduler module and structured slide metadata. No carousel dependency. |
| Five slides | Business discovery, market intelligence, financial planning, scheme guidance and multilingual guidance. AI Advisor is explicitly Coming Soon. |
| Timing and controls | Six-second one-shot timer, previous/next, five indicators, pause/play, arrow keys and horizontal swipe. Manual navigation increments a revision to restart the timer. |
| Pause and cleanup | Hover, focus within the carousel, hidden browser tabs and explicit pause suspend rotation. Effect cleanup cancels timers and removes media/visibility listeners. |
| Reduced motion | Automatic rotation is disabled while reduced motion is enabled; manual controls remain available. Home transitions and shimmer are disabled. The play control cannot override the motion preference. |
| Image loading | First image mounts immediately with high fetch priority. Once the current image settles, only the next image is mounted ahead at low priority. Other image requests are deferred until needed; no upfront five-image preload. |
| Loading feedback | Static text, header and cards render immediately. A subtle top loading shimmer accompanies the image's existing background; loaded photos fade in. No artificial wait or full-screen spinner. |
| Missing images | Local CSS background with field contours and the existing Sprout icon remains visible. Failed image elements are removed; no blank hero or broken-image icon. No raster placeholder assets are generated. |
| Dynamic copy | `landingMessages.ts` participates in the existing `localizeText` lookup and `useUi().text` flow. Duplicate phrases retain existing translations. Slides, services, journey and schemes use centralized content arrays. |
| English | Complete new message catalog and accessible labels. |
| Hindi | Complete new message catalog; existing translated shared labels reused. |
| Marathi | Complete new message catalog; existing translated shared labels reused. |
| Language stability | Locale is separate from carousel index, image state and timer revision. Stable slide IDs avoid remounting on translation changes. UdyamMitra remains the brand name in the new home branding. |
| Quick Access | Four navy service cards with real links: Market Analysis, Business Opportunities, Financial Planning and Government Schemes. |
| Help features | Four icon-led explanations for market evidence, discovery, financial planning and scheme guidance. No fabricated statistics. |
| Journey | Six numbered steps; 3×2 on desktop and a connected vertical list on mobile, outside the hero. |
| Explore | Six service cards, including existing Business Analysis and an explicitly unfinished AI Advisor. |
| Scheme highlights | Micro Finance and Term Loan editorial summaries match the requested scheme-v1 project limits, funding share, loan caps, rates, tenures and moratoria. |
| Scheme data boundary | Canonical definitions remain in `backend/app/scheme_rules.py`; public summaries are centralized in `landingPortal.ts` and translated messages. The available guidance endpoint requires authentication, so the landing page makes no scheme API calls or eligibility calculations. Tests check the current canonical metadata. Keep these editorial summaries synchronized if scheme-v1 changes. |
| Trust | Location evidence, rule-based calculations, transparent scheme guidance, three-language access and the lender/channelizing-authority disclaimer. No official-government affiliation claims. |
| Footer | Brand/prototype explanation, Platform, Financial Guidance, Support, Languages, functioning accessibility anchor/help and existing legal routes. Advisor and Documents are labelled Coming Soon. |
| Animation | 650ms slide crossfade, 500ms image fade, restrained 200ms card/button feedback and image-only shimmer. |
| Responsive layout | Flexible 4/2/1 and 3/2/1 grids; mobile menu at 1100px; stacked phone CTAs and cards; no fixed desktop card widths. Hero grid overlaps all slides and reserves the tallest content, preventing slide-to-slide height changes. |
| Hero sizing | Desktop minimum follows 560px–760px/75vh; tablet minimum 580px; mobile minimum 520px–540px. Content may increase height for Devanagari, large text or narrow screens instead of clipping. |
| Typography | Devanagari-friendly line heights and wrapping, relative font sizes for existing size controls, no aggressive language-specific size reduction. |
| Accessibility | Semantic sections, real links/buttons, labelled carousel/dots/navigation, inactive slides use `inert` and `aria-hidden`, visible focus styles, keyboard-entry focus target, polite manual slide announcements and translated alt text. |
| Performance | No dependencies or images added. Uses existing React and Lucide. Static sections render immediately. Latest full-app output is approximately 1,077 KB JS / 289 KB gzip and 147 KB CSS / 29 KB gzip. The existing 500 KB chunk warning remains. No reliable pre-task bundle delta was recorded. |

## Image handoff

Place your final licensed rural entrepreneurship images in:

`/Users/abhayvijaysonone/Desktop/SIH26091-Web/public/assets/landing/carousel/`

Expected filenames:

- `rural-entrepreneur-woman.webp`
- `rural-kirana-owner.webp`
- `rural-tailoring-business.webp`
- `rural-dairy-entrepreneur.webp`
- `rural-agri-equipment.webp`

Recommended dimensions: **1920×800**, landscape **WebP**, roughly **≤300–500 KB** per image. Keep subjects toward the right to accommodate the text overlay. Update localized alt text to describe the actual images. See the README inside the folder for loading and crop details.

## Files from this task

Created:

- `src/components/landing/HeroCarousel.tsx`
- `src/components/landing/carouselState.ts`
- `src/components/landing/PortalSections.tsx`
- `src/components/landing/LandingFooter.tsx`
- `src/components/landing/landing.css`
- `src/data/landingPortal.ts`
- `src/i18n/landingMessages.ts`
- `tests/landing.test.mjs`
- `public/assets/landing/carousel/README.md`
- `LANDING_REDESIGN.md`

Modified:

- `src/pages/public/HomePage.tsx`: home composition.
- `src/layouts/PublicLayout.tsx`: home-only presentation/footer selection and focusable main target.
- `src/components/layout/PublicHeader.tsx`: optional home navigation/utility behavior; existing defaults preserved.
- `src/components/common/Brand.tsx`: optional home-only brand-name preservation.
- `src/i18n/localize.ts`: register the landing message group. This file was already untracked before the task.

No package manifest, lockfile, backend, authentication provider, router, business module, map or dashboard file was edited by this task. Existing changes in those files remain the user's prior work.

## Validation and remaining checks

- `npm test`: **72 passed**, including new landing SSR, message parity, next/previous/indicator handlers, wraparound, timer scheduling/cleanup, pause predicates, reduced-motion predicates, image-state rendering, locale-stable selection, CTA destinations, scheme metadata and responsive-style checks. Existing map/market/scheme/i18n tests continue passing.
- `npm run lint`: **passed**, no warnings.
- `npm run build`: **passed**, including TypeScript and the existing i18n checks; pre-existing large-chunk warning remains.
- `git diff --check`: **passed**.
- Reviewed the task's frontend diff for unrelated edits. No backend migrations were run.
- These are unit/render/structural checks, not real-browser interaction or screenshot tests. Remaining browser checks: 320, 375, 390, 430, 768, 1024, 1280, 1440 and 1920px in EN/HI/MR; large text/zoom; keyboard and screen-reader announcements; mobile swipe; tab visibility changes; slow/failed image loading; real-photo contrast and focal crops. Browser automation was not available in this session.

No images were generated or downloaded. The authenticated dashboard was not redesigned. No backend APIs, business rules, calculations, database or authentication logic changed. Work stops at the landing page.
