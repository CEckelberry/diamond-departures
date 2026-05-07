import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const layoutPath = new URL('../src/routes/+layout.svelte', import.meta.url);
const navPath = new URL('../src/lib/components/shell/Nav.svelte', import.meta.url);
const footerPath = new URL('../src/lib/components/shell/Footer.svelte', import.meta.url);

async function load(path) {
	return readFile(path, 'utf8');
}

test('layout imports and renders shared nav/footer shell', async () => {
	const src = await load(layoutPath);
	assert.match(src, /import\s+Nav\s+from\s+'\$lib\/components\/shell\/Nav\.svelte'/);
	assert.match(src, /import\s+Footer\s+from\s+'\$lib\/components\/shell\/Footer\.svelte'/);
	assert.match(src, /<Nav\s*\/?\s*>/);
	assert.match(src, /<Footer\s*\/?\s*>/);
	assert.match(src, /<main[\s\S]*\{@render children\(\)\}[\s\S]*<\/main>/);
});

test('nav is fixed top and footer has expected links', async () => {
	const navSrc = await load(navPath);
	const footerSrc = await load(footerPath);

	assert.match(navSrc, /position:\s*fixed/);
	assert.match(navSrc, /top:\s*0/);
	for (const href of ['/', 'https://github.com', '/case-study']) {
		assert.match(navSrc, new RegExp(`href=["']${href}`));
	}

	for (const href of ['/methodology', 'https://github.com', '/about']) {
		assert.match(footerSrc, new RegExp(`href=["']${href}`));
	}
});
