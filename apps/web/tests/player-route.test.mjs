import test from "node:test";
import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";

const routeTsPath = new URL(
	"../src/routes/player/[slug]/+page.ts",
	import.meta.url,
);
const routeSveltePath = new URL(
	"../src/routes/player/[slug]/+page.svelte",
	import.meta.url,
);

test("player slug route files exist", async () => {
	await access(routeTsPath);
	await access(routeSveltePath);
});

test("player route renders board context with Panel and back navigation", async () => {
	const src = await readFile(routeSveltePath, "utf8");
	assert.match(
		src,
		/import\s+Board\s+from\s+'\$lib\/components\/board\/Board\.svelte'/,
	);
	assert.match(
		src,
		/import\s+Panel\s+from\s+'\$lib\/components\/player\/Panel\.svelte'/,
	);
	assert.match(src, /href="\/"|goto\('\/'\)/);
});

test("player route loader derives selected player from slug and entries", async () => {
	const src = await readFile(routeTsPath, "utf8");
	assert.match(src, /params\.slug/);
	assert.match(src, /slugify|toSlug/);
	assert.match(src, /selectedPlayerId/);
	assert.match(src, /fetch\((['"])\/api\/board\?/);
});
