import test from 'node:test';
import assert from 'node:assert/strict';
import { access, readFile } from 'node:fs/promises';

const pagePath = new URL('../src/routes/+page.svelte', import.meta.url);
const boardPath = new URL('../src/lib/components/board/Board.svelte', import.meta.url);
const panelPath = new URL('../src/lib/components/player/Panel.svelte', import.meta.url);
const perfSpecPath = new URL('./perf-busy-ingest.spec.ts', import.meta.url);

async function load(path) {
	return readFile(path, 'utf8');
}

test('page separates seed and stream effects to avoid unnecessary stream churn', async () => {
	const src = await load(pagePath);
	assert.match(src, /let\s+streamView\s*=\s*\$state/);
	assert.match(src, /if \(streamView === data\.boardView && streamSort === data\.boardSort\) return/);
});

test('board row animation path keeps compositor-only transform hints', async () => {
	const src = await load(boardPath);
	assert.match(src, /translateZ\(0\)|transform:\s*translate3d/);
	assert.match(src, /contain:\s*layout\s+paint|contain:\s*paint/);
});

test('player panel uses optimized headshot loading and deferred trend chart hydration', async () => {
	const src = await load(panelPath);
	assert.match(src, /decoding="async"/);
	assert.match(src, /fetchpriority="low"/);
	assert.match(src, /await\s+import\('\.\/TrendChart\.svelte'\)/);
});

test('playwright perf script exists for busy ingest simulation', async () => {
	await access(perfSpecPath);
	const src = await load(perfSpecPath);
	assert.match(src, /@playwright\/test/);
	assert.match(src, /50-cell simultaneous flap|busy ingest/);
});
