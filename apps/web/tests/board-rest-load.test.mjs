import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const pageLoadPath = new URL("../src/routes/+page.ts", import.meta.url);
const pageViewPath = new URL("../src/routes/+page.svelte", import.meta.url);

async function load(path) {
	return readFile(path, "utf8");
}

test("route load fetches /api/board with view and sort params", async () => {
	const src = await load(pageLoadPath);
	assert.match(src, /export\s+const\s+load\s*=/);
	assert.match(src, /fetch\('\/api\/board\?/);
	assert.match(src, /params\.set\('view'/);
	assert.match(src, /params\.set\('sort'/);
});

test("+page consumes load data, passes rows into Board, and shows skeleton while loading", async () => {
	const src = await load(pageViewPath);
	assert.match(src, /let\s*\{\s*data\s*\}:\s*\{\s*data:/);
	assert.match(src, /<Board\s+rows=\{boardRows\}/);
	assert.match(src, /\{#if\s+isLoading\}/);
	assert.match(src, /class=['"]board-skeleton['"]/);
});
