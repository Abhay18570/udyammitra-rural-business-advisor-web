# Landing motion and carousel copy

## Audit

The working tree was clean at the start. Inspected status, full diff and diff statistics, public layout/header/footer, carousel/image state, slide metadata, landing sections, shared loading UI, language lookup, responsive styles and reduced-motion rules.

Existing motion: 650ms slide crossfade, 500ms image fade, image-loading shimmer, simple card/button hover and indicator transitions. Headings, sections, journey, trust and footer appeared immediately with no entrance effects. Hero copy already changed by slide/language but had no highlight, supporting line or staged text entrance. Hero photographs were the only actual asynchronous content; landing cards and text were static.

## Changes

- Added `useRevealOnScroll` / `observeReveals`: one IntersectionObserver per home mount, with one-time reveals and cleanup. Related items stagger by 60ms, capped at 300ms for six items. Visible content is the default: there is no hidden/preload state, observer timer or render gate. Missing IntersectionObserver and reduced motion skip observer setup. Scrolling back and forth does not replay a revealed item.
- Navbar: subtle utility-bar fade, small navigation-row entrance, logo scale from .96, link stagger and Get Started entrance. Existing dimensions, image variants, links, mobile controls and interactivity remain.
- Hero: existing navy fallback/image loading retained. Readable overlay stays at least 95% of its normal strength during entrance. Eyebrow, headline, highlight, description and CTAs enter in that order over roughly 650ms. Controls fade on initial mount. Outgoing copy fades in 150ms while the original carousel crossfade continues. Language changes do not remount slides or restart the autoplay effect.
- Images: first image remains eager/high-priority; only the next image is warmed after the current image settles. Loaded photos fade in. Failed images retain the existing styled fallback. No image pipeline or logo edits.
- Data: each slide now has eyebrow, title, highlight, description, primary action/route, secondary action/anchor and supporting line. All displayed copy passes through existing runtime localization.
- Supporting lines are deliberately static per slide. The optional independent 2–3 second micro-text rotation was not added; no second timer competes with reading the five-slide carousel.
- Quick Access: staggered entrance, existing elevation plus small icon scale and arrow movement. Essential information remains visible without hover.
- Help/Explore: headings reveal once; cards stagger. Help icons scale subtly inside their card entrance.
- Journey: six sequential staggered reveals; existing desktop grid/mobile vertical connection remains. No additional SVG or line-animation machinery.
- Scheme cards: slight stagger, hover elevation and border emphasis. Keyboard focus on the shared scheme CTA emphasizes its cards; CTA arrows move on hover. Financial values remain static.
- Trust/footer: individual trust-point fade; a single restrained footer fade rather than separate link animations.
- CTA interactions: hover feedback, slight press effect and clear focus outline. Focusing interactive/reveal content cancels entrance animations where necessary so keyboard use is immediate.

## Five messages

| Slide | Main headline | Highlight | Primary CTA |
| --- | --- | --- | --- |
| Rural Business Discovery | Find the Right Business for Your Local Market | Before You Invest | Explore Opportunities → `/opportunities` |
| Hyper-Local Market Evidence | See What Businesses Exist Around You | Within 1–10 km | Analyze My Market → `/market-analysis` |
| Smart Financial Planning | Turn Your Contribution Into a Practical Business Plan | Know Your Funding Need | Create Financial Plan → `/financial-plan` |
| Government Scheme Guidance | Understand the Financing Path That Fits Your Project | Micro Finance or Term Loan | Check Scheme Guidance → `/schemes` |
| Business Guidance in Your Language | Plan Your Business With Clear Local Guidance | English • हिंदी • मराठी | Get Started → `/register` |

Every slide has the existing How It Works anchor as its secondary CTA. Slide five now describes implemented multilingual guidance and links to the existing registration flow, as requested; it does not claim a live AI advisor. The separate Explore AI Advisor card remains Coming Soon. No route definitions changed.

## Loading, language and accessibility

Static text/cards render immediately. Shimmer remains exclusive to genuinely pending hero images. No artificial loading screen, 1–2 second wait, fake navigation spinner, lazy-section delay or new asynchronous content was added.

English, Hindi and Marathi cover all new eyebrows, titles, highlights, descriptions and supporting lines. Existing translated CTA labels are reused. Duplicate phrases share the established translations. Stable slide IDs and separate carousel state preserve selection and autoplay timing during language changes.

Reduced motion disables reveal/text animations, shimmer, transforms and carousel autoplay. Content remains visible and manual controls remain available. No animation communicates unique information; semantic markup, inert inactive slides, accessible labels and keyboard controls remain.

Responsive layouts remain fluid, with wrapping highlights/descriptions, Devanagari line-height support, existing stacked mobile CTAs and a hero grid reserving space for the tallest slide. Entrance transforms use vertical movement or a small inward scale, avoiding horizontal reveal overflow. No fixed text height, per-letter animation or clipping mask was introduced.

## Performance

No dependencies or frameworks added. One small observer hook, CSS keyframes and translated copy. No continuous animation beyond the existing loading shimmer while images are pending; no micro-text timer.

Full-app build is approximately 1,086 KB JS / 290.3 KB gzip and 153 KB CSS / 30.5 KB gzip. Compared with the preceding build, the added compressed JS is about 1.6 KB and CSS about 0.8 KB. The existing large-chunk warning remains.

## Files

Created:

- `src/components/landing/useRevealOnScroll.ts`
- `tests/landingMotion.test.mjs`
- `LANDING_MOTION.md`

Modified:

- `src/layouts/PublicLayout.tsx`
- `src/components/landing/HeroCarousel.tsx`
- `src/components/landing/PortalSections.tsx`
- `src/components/landing/LandingFooter.tsx`
- `src/components/landing/landing.css`
- `src/data/landingPortal.ts`
- `src/i18n/landingMessages.ts`
- `tests/landing.test.mjs`

## Validation

- `npm test`: **86 passed**. New tests exercise observer callbacks, stagger order, reveal-once behavior, cleanup, missing-observer/reduced-motion fallbacks, immediate static rendering, and all five localized highlights/support lines/CTAs. Existing image loading/fallback, carousel controls, timer cleanup/autoplay, language-stability and route tests continue passing.
- `npm run lint`: **passed**, no warnings.
- `npm run build`: **passed**, including TypeScript and existing i18n validation. Existing bundle warning remains.
- `git diff --check`: **passed**.
- Final diff/status reviewed; no changes in backend, API/service files, route definitions, authentication, business modules, calculations, map logic or package dependencies.

Tests are unit/render/structural tests, not real-browser screenshots. Live viewport checks at 320, 375, 390, 430, 768, 1024, 1280, 1440 and 1920px remain unverified because browser automation was unavailable in this session. The remaining visual check is text wrapping/control reachability in EN/HI/MR and reduced-motion mode at those sizes.

No backend/business logic changed. No artificial loading delay was added. No other module was started.
