import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const boardPath = new URL('../src/lib/components/board/Board.svelte', import.meta.url);

async function loadBoard() {
	return readFile(boardPath, 'utf8');
}

test('board uses keyed rows + FLIP animate directive for reshuffles', async () => {
	const src = await loadBoard();
	assert.match(src, /from\s+'svelte\/animate'/);
	assert.match(src, /animate:flip=/);
	assert.match(src, /\{#each\s+placeholderRows\s+as\s+row,\s*index\s*\(row\.playerId\)\}/);
});

test('board defines stagger delay and reduced-motion fallback for row movement', async () => {
	const src = await loadBoard();
	assert.match(src, /index\s*\*\s*30/);
	assert.match(src, /prefers-reduced-motion:\s*reduce/);
	assert.match(src, /duration:\s*reducedMotion\s*\?\s*0/);
});

test('board plays row-shift audio once when rank order changes', async () => {
	const src = await loadBoard();
	assert.match(src, /import\s+\{\s*playRowShift\s*\}\s+from\s+'\$lib\/audio\/flap'/);
	assert.match(src, /playRowShift\(/);
	assert.match(src, /previousOrder/);
});
