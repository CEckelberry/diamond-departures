import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const storePath = new URL('../src/lib/stores/board.ts', import.meta.url);
const typesPath = new URL('../src/lib/components/board/types.ts', import.meta.url);
const boardPath = new URL('../src/lib/components/board/Board.svelte', import.meta.url);
const rowPath = new URL('../src/lib/components/board/Row.svelte', import.meta.url);

async function load(path) {
	return readFile(path, 'utf8');
}

test('board delta/store contract includes newly_qualified signal fields', async () => {
	const src = await load(storePath);
	assert.match(src, /newly_qualified/);
	assert.match(src, /qualified_at/);
	assert.match(src, /justQualified/);
});

test('board row shape includes just-qualified metadata', async () => {
	const src = await load(typesPath);
	assert.match(src, /justQualified\??:\s*boolean/);
	assert.match(src, /qualifiedAt\??:\s*string\s*\|\s*null/);
});

test('row renders just-qualified badge and fade class', async () => {
	const src = await load(rowPath);
	assert.match(src, /just qualified/);
	assert.match(src, /just-qualified-badge/);
	assert.match(src, /--badge-fade-duration/);
});

test('board applies enter animation class for newly-qualified rows', async () => {
	const src = await load(boardPath);
	assert.match(src, /row-enter|just-qualified-enter/);
	assert.match(src, /800ms/);
});
