import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const sseApiPath = new URL("../src/lib/api/sse.ts", import.meta.url);
const boardStorePath = new URL("../src/lib/stores/board.ts", import.meta.url);
const pagePath = new URL("../src/routes/+page.svelte", import.meta.url);

async function load(path) {
	return readFile(path, "utf8");
}

test("SSE client opens /api/board/sse stream and handles snapshot + delta with reconnect", async () => {
	const src = await load(sseApiPath);
	assert.match(src, /export\s+function\s+openBoardStream/);
	assert.match(src, /new\s+EventSource\((['"])/);
	assert.match(src, /\/api\/board\/sse\?/);
	assert.match(src, /addEventListener\((['"])snapshot/);
	assert.match(src, /addEventListener\((['"])delta/);
	assert.match(src, /setTimeout\(/);
	assert.match(src, /Math\.min\(/);
});

test("board store exposes snapshot/delta mutators and rank/stat patching", async () => {
	const src = await load(boardStorePath);
	assert.match(src, /export\s+function\s+applySnapshot/);
	assert.match(src, /export\s+function\s+applyDelta/);
	assert.match(src, /player_id/);
	assert.match(src, /new_rank/);
	assert.match(src, /stat_value/);
	assert.match(src, /sort\(/);
});

test("page wires stream in onMount and closes stream on teardown", async () => {
	const src = await load(pagePath);
	assert.match(src, /import\s+\{\s*onMount\s*\}\s+from\s+'svelte'/);
	assert.match(src, /openBoardStream\(/);
	assert.match(src, /applySnapshot\(/);
	assert.match(src, /applyDelta\(/);
	assert.match(src, /return\s*\(\)\s*=>\s*\{\s*stop\(\)/);
});
