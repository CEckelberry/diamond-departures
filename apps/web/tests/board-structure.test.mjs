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
	for (const label of ['RK', 'PLAYER', 'TEAM', 'POS', 'STAT']) {
		assert.match(src, new RegExp(`>${label}<`));
	}
	assert.match(src, /placeholderRows\s*=\s*\$derived/);
	assert.match(src, /Array\.from\(\{\s*length:\s*100\s*\}/);
	assert.match(src, /aria-label=['"]leaderboard board['"]/);
});

test('row composes flap words for each board column with 36px row height', async () => {
	const src = await load(rowPath);
	assert.match(src, /import\s+Word\s+from\s+'\$lib\/components\/flap\/Word\.svelte'/);
	for (const name of ['rank', 'player', 'team', 'position', 'stat']) {
		assert.match(src, new RegExp(`value={row.${name}}`));
	}
	assert.match(src, /height:\s*36px/);
	assert.match(src, /grid-template-columns:\s*3\.5rem\s+20rem\s+6rem\s+6rem\s+8rem/);
});
