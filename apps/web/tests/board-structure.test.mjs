import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const boardPath = new URL('../src/lib/components/board/Board.svelte', import.meta.url);
const rowPath = new URL('../src/lib/components/board/Row.svelte', import.meta.url);

async function load(path) {
	return readFile(path, 'utf8');
}

test('board defines fixed header columns and 100-row placeholder render', async () => {
	const src = await load(boardPath);
	for (const label of ['RK', 'PLAYER', 'TEAM', 'POS']) {
		assert.match(src, new RegExp(`>${label}<`));
	}
	// Dynamic stat columns driven by style (saber/traditional) and view (hitters/pitchers)
	assert.match(src, /HITTER_TRAD_COLS/);
	assert.match(src, /HITTER_SABER_COLS/);
	assert.match(src, /PITCHER_TRAD_COLS/);
	assert.match(src, /PITCHER_SABER_COLS/);
	assert.match(src, /statCols\s*=\s*\$derived/);
	assert.match(src, /placeholderRows\s*=\s*\$derived/);
	assert.match(src, /Array\.from\(\{\s*length:\s*100\s*\}/);
	assert.match(src, /aria-label=['"]leaderboard board['"]/);
});

test('row composes flap words for each board column with correct grid layout', async () => {
	const src = await load(rowPath);
	assert.match(src, /import\s+Word\s+from\s+'\$lib\/components\/flap\/Word\.svelte'/);
	for (const name of ['rank', 'player', 'team', 'position']) {
		assert.match(src, new RegExp(`value={row.${name}}`));
	}
	// Multi-stat loop: stat values come from row.stats[statName]
	assert.match(src, /row\.stats\[statName\]/);
	// Grid: 3.5rem rank + 21rem player + 5rem team + 4rem pos + 7 stat cols
	assert.match(src, /grid-template-columns:\s*3\.5rem\s+21rem\s+5rem\s+4rem\s+repeat\(7,\s*5\.5rem\)/);
});
