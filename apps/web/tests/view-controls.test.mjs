import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const tabsPath = new URL('../src/lib/components/board/ViewTabs.svelte', import.meta.url);
const statPickerPath = new URL('../src/lib/components/board/StatPicker.svelte', import.meta.url);

async function load(path) {
	return readFile(path, 'utf8');
}

test('view tabs sync URL params and position dropdown behavior', async () => {
	const src = await load(tabsPath);
	assert.match(src, /from\s+'\$app\/navigation'/);
	assert.match(src, /goto\(/);
	assert.match(src, /params\.set\('view'/);
	assert.match(src, /params\.set\('position'/);
	assert.match(src, /document\.addEventListener\('click'/);
	assert.match(src, /dropdownOpen\s*=\s*false/);
});

test('stat picker switches stat families by view and syncs sort param', async () => {
	const src = await load(statPickerPath);
	assert.match(src, /const\s+HITTER_STATS\s*=\s*\[/);
	assert.match(src, /const\s+PITCHER_STATS\s*=\s*\[/);
	assert.match(src, /derivedStats\s*=\s*\$derived/);
	assert.match(src, /params\.set\('sort'/);
	assert.match(src, /overflow-x:\s*auto/);
});
