import test from "node:test";
import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";

const seoPath = new URL(
	"../src/lib/components/shell/SEO.svelte",
	import.meta.url,
);
const homePath = new URL("../src/routes/+page.svelte", import.meta.url);
const robotsPath = new URL(
	"../src/routes/robots.txt/+server.ts",
	import.meta.url,
);
const sitemapPath = new URL(
	"../src/routes/sitemap.xml/+server.ts",
	import.meta.url,
);
const ogPath = new URL("../src/routes/og/top3.svg/+server.ts", import.meta.url);

test("seo component exists and is used on home route", async () => {
	await access(seoPath);
	const home = await readFile(homePath, "utf8");
	assert.match(home, /import SEO from '\$lib\/components\/shell\/SEO\.svelte'/);
	assert.match(home, /<SEO/);
	assert.match(home, /title="Diamond Departures · Live Board"/);
});

test("robots and sitemap routes are present", async () => {
	const robots = await readFile(robotsPath, "utf8");
	const sitemap = await readFile(sitemapPath, "utf8");
	assert.match(robots, /User-agent:\s\*/);
	assert.match(robots, /Sitemap:/);
	assert.match(sitemap, /<urlset/);
	assert.match(sitemap, /\/methodology/);
});

test("og top3 svg route is present and returns svg metadata shell", async () => {
	const src = await readFile(ogPath, "utf8");
	assert.match(src, /content-type': 'image\/svg\+xml/);
	assert.match(src, /Today’s top 3 hitters/);
	assert.match(src, /fetch\('\/api\/board\?view=hitters&sort=wrc_plus'\)/);
});
