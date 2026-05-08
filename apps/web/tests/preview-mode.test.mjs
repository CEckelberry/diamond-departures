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

test("header exposes preview mode controls in off-season state", async () => {
	const src = await load(headerPath);
	assert.match(src, /Preview mode/);
	assert.match(src, /preview running|Preview running/);
	assert.match(src, /onTogglePreview|togglePreview/);
});

test("board page tracks preview mode state and replay label", async () => {
	const src = await load(pagePath);
	assert.match(src, /previewMode\s*=\s*\$state/);
	assert.match(src, /preview running|Replay mode/);
	assert.match(src, /<Header\s+previewRunning=\{previewMode\}/);
});

test("SSE wiring supports preview endpoint /api/board/preview-sse", async () => {
	const pageSrc = await load(pagePath);
	const sseSrc = await load(ssePath);
	assert.match(pageSrc, /\/api\/board\/preview-sse/);
	assert.match(sseSrc, /endpoint\??/);
});
