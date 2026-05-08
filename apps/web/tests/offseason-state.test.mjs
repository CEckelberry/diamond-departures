import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const headerPath = new URL('../src/lib/components/board/Header.svelte', import.meta.url);
const pagePath = new URL('../src/routes/+page.svelte', import.meta.url);

async function load(path) {
	return readFile(path, 'utf8');
}

test('header includes off-season final banner and countdown copy', async () => {
	const src = await load(headerPath);
	assert.match(src, /off-season/);
	assert.match(src, /regular season · final/);
	assert.match(src, /next season/i);
});

test('board page suppresses SSE stream when season mode is off-season', async () => {
	const src = await load(pagePath);
	assert.match(src, /fetch\('\/api\/season-state'\)/);
	assert.match(src, /seasonMode\s*===\s*'off-season'/);
	assert.match(src, /openBoardStream\(/);
});

test('stat picker remains wired in board page for off-season sorting', async () => {
	const src = await load(pagePath);
	assert.match(src, /<StatPicker\s+\{view\}\s*\/>/);
});
