import test from 'node:test';
import assert from 'node:assert/strict';

import { buildCells, diffCells, isNumericWord } from '../src/lib/components/flap/word.mjs';

test('isNumericWord detects score-like values', () => {
	assert.equal(isNumericWord('172'), true);
	assert.equal(isNumericWord('-12.3'), true);
	assert.equal(isNumericWord('Judge'), false);
});

test('buildCells right-aligns numeric values', () => {
	assert.deepEqual(buildCells('98', 5), [' ', ' ', ' ', '9', '8']);
	assert.deepEqual(buildCells('172', 5), [' ', ' ', '1', '7', '2']);
});

test('buildCells left-aligns text values', () => {
	assert.deepEqual(buildCells('JUDGE', 8), ['J', 'U', 'D', 'G', 'E', ' ', ' ', ' ']);
});

test('diffCells marks only changed positions', () => {
	const from = [' ', ' ', '9', '8'];
	const to = [' ', '1', '7', '2'];
	assert.deepEqual(diffCells(from, to), [1, 2, 3]);
});
