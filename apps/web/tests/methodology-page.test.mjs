import test from 'node:test';
import assert from 'node:assert/strict';
import { access, readFile } from 'node:fs/promises';

const methodologyPath = new URL('../src/routes/methodology/+page.svelte', import.meta.url);
const footerPath = new URL('../src/lib/components/shell/Footer.svelte', import.meta.url);

test('methodology route file exists', async () => {
	await access(methodologyPath);
});

test('methodology page links to source docs and repository', async () => {
	const src = await readFile(methodologyPath, 'utf8');
	assert.match(src, /DATA\.md/);
	assert.match(src, /STATS\.md/);
	assert.match(src, /github\.com\/CEckelberry\/diamond-departures/);
	assert.match(src, /<h1>Methodology<\/h1>/);
});

test('footer exposes visible methodology link', async () => {
	const src = await readFile(footerPath, 'utf8');
	assert.match(src, /href="\/methodology"/);
});
