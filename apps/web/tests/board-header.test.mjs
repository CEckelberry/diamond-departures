import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const headerPath = new URL(
	"../src/lib/components/board/Header.svelte",
	import.meta.url,
);

async function loadHeader() {
	return readFile(headerPath, "utf8");
}

test("header declares mode classes and live pulse behavior", async () => {
	const src = await loadHeader();
	assert.match(src, /const\s+MODE_CLASS\s*=\s*\{/);
	for (const mode of ["live", "between", "off-game", "off-season"]) {
		assert.match(src, new RegExp(`['"]?${mode}['"]?:`));
	}
	assert.match(src, /animate-pulse/);
});

test("header fetches status/freshness and exposes sound toggle + debug panel", async () => {
	const src = await loadHeader();
	assert.match(src, /fetch\('\/api\/season-state'\)/);
	assert.match(src, /fetch\('\/api\/freshness'\)/);
	assert.match(
		src,
		/import\s+\{\s*soundEnabled\s*,\s*setSoundEnabled\s*\}\s+from\s+'\$lib\/stores\/sound'/,
	);
	assert.match(src, /onclick=\{toggleSound\}/);
	assert.match(src, /onclick=\{toggleFreshnessDebug\}/);
	assert.match(src, /<FreshnessPanel/);
});
