import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const pageLoadPath = new URL('../src/routes/+page.ts', import.meta.url);
const pageViewPath = new URL('../src/routes/+page.svelte', import.meta.url);

async function load(path) {
	return readFile(path, 'utf8');
}

test('+page load resolves position mode into apiView and selected position output', async () => {
	const src = await load(pageLoadPath);
	assert.match(src, /type\s+ViewResolution\s*=\s*\{/);
	assert.match(src, /apiView:\s*string/);
	assert.match(src, /selectedPosition:\s*string/);
	assert.match(src, /function\s+resolveView\(params: URLSearchParams\): ViewResolution/);
	assert.match(src, /return\s*\{\s*apiView:\s*'hitters_ss',\s*selectedPosition:\s*'SS'/);
	assert.match(src, /selectedPosition:\s*resolvedView\.selectedPosition/);
});

test('+page view filters board rows by selected position and renders filteredRows', async () => {
	const src = await load(pageViewPath);
	assert.match(src, /selectedPosition:\s*string/);
	assert.match(src, /const\s+filteredRows\s*=\s*\$derived/);
	assert.match(src, /if\s*\(view\s*!==\s*'positions'\s*\|\|\s*!selectedPosition\s*\|\|\s*selectedPosition\s*===\s*'all'\)/);
	assert.match(src, /row\.position\s*===\s*selectedPosition/);
	assert.match(src, /<Board\s+rows=\{filteredRows\}/);
});
