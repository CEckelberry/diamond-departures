# P7-04 verification (SEO + Open Graph)

Date: 2026-05-08

## RED

- Added SEO/OG contract test file: `apps/web/tests/seo-og.test.mjs`.

## GREEN

- `node --test apps/web/tests/seo-og.test.mjs` → PASS

## Implemented

- Added reusable SEO head component: `apps/web/src/lib/components/shell/SEO.svelte`.
- Added robots route: `apps/web/src/routes/robots.txt/+server.ts`.
- Added sitemap route: `apps/web/src/routes/sitemap.xml/+server.ts`.
- Added dynamic OG SVG endpoint: `apps/web/src/routes/og/top3.svg/+server.ts`.
- Applied SEO component on layout/home and player pages.
