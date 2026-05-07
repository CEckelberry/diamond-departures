import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const routePath = new URL('../src/routes/test/flap/+page.svelte', import.meta.url);

async function loadPage() {
	return readFile(routePath, 'utf8');
}

test('test flap route exists and is dev-gated', async () => {
	const src = await loadPage();
	assert.match(src, /import\s+\{\s*dev\s*\}\s+from\s+'\$app\/environment'/);
	assert.match(src, /\{#if\s+dev\}/);
});

test('test flap route includes required control IDs', async () => {
	const src = await loadPage();
	for (const id of ['single', 'word', 'storm', 'row-shift']) {
		assert.match(src, new RegExp(`id=["']${id}["']`));
	}
});
