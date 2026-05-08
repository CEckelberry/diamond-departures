import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const rowPath = new URL('../src/lib/components/board/Row.svelte', import.meta.url);
const boardPath = new URL('../src/lib/components/board/Board.svelte', import.meta.url);
const pagePath = new URL('../src/routes/+page.svelte', import.meta.url);


test('row supports keyboard activation and explicit aria label', async () => {
	const src = await readFile(rowPath, 'utf8');
	assert.match(src, /role="button"/);
	assert.match(src, /tabindex="0"/);
	assert.match(src, /onkeydown=\{handleKeydown\}/);
	assert.match(src, /aria-label=\{rowAriaLabel\}/);
	assert.match(src, /event\.key === 'Enter' \|\| event\.key === ' '/);
});

test('board live region is polite for flap updates', async () => {
	const src = await readFile(boardPath, 'utf8');
	assert.match(src, /aria-live="polite"/);
});

test('escape closes the player panel from board route', async () => {
	const src = await readFile(pagePath, 'utf8');
	assert.match(src, /event\.key === 'Escape'/);
	assert.match(src, /selectedPlayerId = null/);
	assert.match(src, /onclose=\{closePanel\}/);
});
