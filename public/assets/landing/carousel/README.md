Place your final licensed rural entrepreneurship images in this folder:

`public/assets/landing/carousel/`

Expected filenames (case-sensitive):

- `rural-entrepreneur-woman.webp`
- `rural-kirana-owner.webp`
- `rural-tailoring-business.webp`
- `rural-dairy-entrepreneur.webp`
- `rural-agri-equipment.webp`

Use landscape WebP images around **1920 × 800 pixels**, preferably **300–500 KB or less** each. Keep the main subject towards the right; the left side carries the text overlay. Cropping uses `object-fit: cover` and `object-position: 70% center`. Check the crop on phones before publishing. To use AVIF, update the filenames in `src/data/landingPortal.ts`.

Public URL prefix: `/assets/landing/carousel/`. No imports or rebuild configuration are needed; Vite serves/copies these public assets automatically.

No photos are bundled. Until you provide them, the carousel renders its original CSS background, field contours and existing Sprout icon. Missing images do not break the build. Alt text is stored in `src/i18n/landingMessages.ts`; update it to accurately describe the photos you supply in all three languages.

The first image is requested immediately with high priority. After the current image loads or fails, only its next neighbour is mounted ahead of time at low priority. Later images are deferred until needed. Successful images fade in; failed images retain the CSS background without a broken-image icon.
