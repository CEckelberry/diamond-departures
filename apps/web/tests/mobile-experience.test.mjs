import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const rowPath = new URL('../src/lib/components/board/Row.svelte', import.meta.url);
const boardPath = new URL('../src/lib/components/board/Board.svelte', import.meta.url);
const appCssPath = new URL('../src/app.css', import.meta.url);

test('row has mobile card layout and tap-target sizing', async () => {
	const src = await readFile(rowPath, 'utf8');
	assert.match(src, /min-height:\s*44px/);
	assert.match(src, /@media \(max-width: 920px\)/);
	assert.match(src, /grid-template-columns:\s*1fr/);
});

test('board header is hidden on mobile and spacing adapts', async () => {
	const src = await readFile(boardPath, 'utf8');
	assert.match(src, /@media \(max-width: 920px\)/);
	assert.match(src, /\.board-header-row\s*\{\s*display: none;/);
});

test('global styles prevent horizontal overflow', async () => {
	const src = await readFile(appCssPath, 'utf8');
	assert.match(src, /overflow-x:\s*hidden/);
});
