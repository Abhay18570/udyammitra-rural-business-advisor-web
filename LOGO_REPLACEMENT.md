# UdyamMitra logo replacement

- Original: `tests/logo/UdyamMitra_Logo.jpeg` (1254×1254, 152,772 bytes).
- Final production path: `public/assets/branding/udyammitra-logo.jpeg`. The original was moved, so there is no duplicate under tests. The final asset has been staged in Git as requested; no other pre-existing changes were staged.
- SHA-256 before and after: `58691f264361b5975050cdbf561c4901fb5b5324622aa29b0895d649410cf66b`. The image bytes, artwork, colors and white background are unchanged.
- Reusable component: `src/components/common/UdyamMitraLogo.tsx`, with small/medium/large sizes, optional class name, explicit dimensions, eager loading, `object-fit: contain` and square aspect ratio. Standalone alt text is `UdyamMitra`; decorative use beside visible brand text has empty alt text.
- Replaced the Lucide Sprout in the shared `Brand`, landing footer and carousel fallback brand seal. The old sprout SVG favicon was removed and the favicon reference now uses the same production JPEG.
- Public header/mobile navigation: the image replaces the green square/sprout; existing brand text, tagline, routes and menu behavior remain. Shared header image is 56px on desktop and 46px on narrow screens. The image does not shrink; adjacent text can wrap.
- Login, registration and forgot-password branding inherits the new image through the existing `AuthLayout` and `Brand`. Forms and authentication behavior were not edited.
- Dashboard expanded sidebar, mobile drawer, admin sidebar and standard footer inherit the new image through `Brand`. Sidebar logos use 48px presentation and a white surface.
- Collapsed sidebar: the original brand-mark wrapper and label-hiding selectors remain in place. The 48px logo fits within the 76px sidebar with its existing padding, and the home link retains its accessible label and now has a title tooltip. Collapse state, controls, persistence and drawer behavior were not edited.
- Feature icons: the audit found no other Sprout/Leaf feature usages. All ordinary capability, navigation and service icons were retained; no global icon replacement was performed. No separate loading/skeleton logo was found. Onboarding inherits the dashboard shell branding.

Created:

- `public/assets/branding/udyammitra-logo.jpeg` (moved supplied asset; tracked/staged)
- `src/components/common/UdyamMitraLogo.tsx`
- `tests/branding.test.mjs`
- `LOGO_REPLACEMENT.md`

Modified:

- `src/components/common/Brand.tsx`
- `src/components/landing/LandingFooter.tsx`
- `src/components/landing/HeroCarousel.tsx` (brand symbol only)
- `src/responsive.css` (logo presentation only)
- `index.html` (favicon reference)
- `tests/landing.test.mjs` (photo assertions now distinguish carousel photos from brand images)

Removed/moved:

- `tests/logo/UdyamMitra_Logo.jpeg` → production path above
- `public/favicon.svg` (obsolete sprout favicon)

Validation:

- `npm test`: 79 passed. New tests cover exact asset integrity, accessible image modes, header/auth/footer logo rendering in EN/HI/MR, expanded and persisted collapsed dashboard rendering, preserved collapse controls, favicon reference and aspect-ratio CSS. Existing landing tests were adjusted to count photographs rather than all image elements.
- `npm run lint`: passed without warnings.
- `npm run build`: passed; existing large-bundle warning remains. No dependency added.
- `git diff --check`: passed. Inspected final diff/status; existing unrelated working-tree changes remain intact.
- Responsive behavior was checked through markup, existing layout selectors and logo-specific CSS. Real-browser screenshots at 320/375/390/430/768/1024/1280/1440px were not available in this session, so visual fit across that matrix remains a manual check.

No landing redesign, backend changes, business-logic changes, authentication changes, route changes, or module changes were made. No logo was generated, downloaded, recolored, cropped or otherwise edited.
