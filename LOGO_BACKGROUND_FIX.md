# Logo background fix

Original light-surface asset: `public/assets/branding/udyammitra-logo.jpeg`.
Transparent dark-surface asset: `public/assets/branding/udyammitra-logo-transparent.png`.

The JPEG was decoded locally with macOS `sips`. A dependency-free Python flood fill selected near-white pixels connected to the outer image boundary (all RGB channels ≥235, channel spread ≤22). Only that background became transparent. Enclosed light regions were not selected; retained artwork pixels keep their decoded RGB values and full opacity. Fully transparent pixels have zeroed RGB for smaller compression. No recoloring, cropping, replacement artwork, AI generation, external images, blend modes, filters or masks were used.

Inspected a dark-navy composite of the result: hand, fields, house, sun, plant and circular elements remain intact; background-connected negative spaces are transparent. The source JPEG remains byte-identical (SHA-256 `58691f264361b5975050cdbf561c4901fb5b5324622aa29b0895d649410cf66b`). The PNG retains the full 1254×1254 canvas.

`UdyamMitraLogo` now accepts `variant="light"` (default) or `variant="transparent"`. Accessible alt/decorative behavior, eager loading and dimensions remain. `Brand` chooses transparent for its existing inverse/dark mode.

- **White navbar:** original JPEG, size, alignment, white background, text, responsive rules and favicon unchanged.
- **Hero:** transparent PNG, no white image/container background, no logo opacity trick. Logo width is 104px desktop, 90px tablet and 72px mobile, with `height: auto` and `object-fit: contain`.
- **Other dark areas:** auth side panel, dashboard expanded/collapsed sidebar and mobile drawer, admin sidebar, standard footer and landing footer use transparent branding. Existing wrapper dimensions and collapse behavior remain.
- **Carousel:** slide count, content, translations, CTAs, state, timing, controls and transitions unchanged. Only its branding asset, dimensions and prior seal-opacity declarations changed.
- **Feature icons:** untouched. No separate splash/loading brand logo was found.

Created:

- `public/assets/branding/udyammitra-logo-transparent.png`
- `LOGO_BACKGROUND_FIX.md`

Modified:

- `src/components/common/UdyamMitraLogo.tsx`
- `src/components/common/Brand.tsx`
- `src/components/landing/HeroCarousel.tsx`
- `src/components/landing/LandingFooter.tsx`
- `src/components/landing/landing.css`
- `src/responsive.css`
- `tests/branding.test.mjs`

Validation: `npm test` **80 passed**; `npm run lint` **passed**; `npm run build` **passed** with the existing bundle warning; `git diff --check` **passed**. Reviewed logo usages and working-tree status/diff. Tests distinguish unchanged light-navbar branding from transparent dark-layout branding and verify the PNG alpha format. Existing carousel and multilingual tests pass.

The processed artwork was visually inspected on dark navy. Live-browser checks across 320/375/390/430/768/1024/1280/1440px were not available; responsive CSS and rendered markup were checked, but that screenshot matrix remains unverified.

No backend, business logic, authentication, routes, feature content or other modules changed.
