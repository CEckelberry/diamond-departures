import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const headerPath = new URL(
	"../src/lib/components/board/Header.svelte",
	import.meta.url,
);
const pagePath = new URL("../src/routes/+page.svelte", import.meta.url);
const ssePath = new URL("../src/lib/api/sse.ts", import.meta.url);

async function load(path) {
	return readFile(path, "utf8");
}

test("header shows between-games/no-games-today idle copy with next-game ETA", async () => {
	const src = await load(headerPath);
	assert.match(src, /No games until/);
	assert.match(src, /No games today/);
	assert.match(src, /in\s*\$\{.*hours/);
});

test("board page keeps SSE open outside off-season and passes idle-mode option", async () => {
	const src = await load(pagePath);
	assert.match(src, /seasonMode\s*!==\s*'off-season'/);
	assert.match(src, /idleMode/);
	assert.match(src, /openBoardStream\(/);
});

test("SSE client supports slower reconnect policy for idle states", async () => {
	const src = await load(ssePath);
	assert.match(src, /idleMode\??:\s*boolean/);
	assert.match(src, /120000|60000/);
	assert.match(src, /reconnect|delay/);
});
