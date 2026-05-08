import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const panelPath = new URL('../src/lib/components/board/FreshnessPanel.svelte', import.meta.url);
const headerPath = new URL('../src/lib/components/board/Header.svelte', import.meta.url);

async function load(path) {
	return readFile(path, 'utf8');
}

test('freshness panel exists and fetches /api/freshness', async () => {
	const src = await load(panelPath);
	assert.match(src, /fetch\('\/api\/freshness'\)/);
	assert.match(src, /role="dialog"/);
	assert.match(src, /aria-label="Freshness debug panel"/);
});

test('panel renders ingest runs, per-stat freshness, and schema drift sections', async () => {
	const src = await load(panelPath);
	assert.match(src, /Ingest runs|Last ingest runs/);
	assert.match(src, /Per-stat freshness/);
	assert.match(src, /Schema drift/);
});

test('header uses FreshnessPanel component instead of placeholder debug panel copy', async () => {
	const src = await load(headerPath);
	assert.match(src, /import\s+FreshnessPanel\s+from\s+'\$lib\/components\/board\/FreshnessPanel\.svelte'/);
	assert.match(src, /<FreshnessPanel/);
	assert.doesNotMatch(src, /Placeholder modal for expanded freshness diagnostics/);
});
