import test from 'node:test';
import assert from 'node:assert/strict';

import { FLIP_TIMINGS, enqueueGlyph, normalizeGlyph, shouldFlash } from '../src/lib/components/flap/animation.mjs';

test('normalizeGlyph keeps one uppercased character', () => {
	assert.equal(normalizeGlyph('mvp'), 'M');
	assert.equal(normalizeGlyph(''), ' ');
	assert.equal(normalizeGlyph(undefined), ' ');
});

test('flip timings follow 3-phase 450ms sequence', () => {
	assert.deepEqual(FLIP_TIMINGS, {
		topMs: 150,
		pauseMs: 120,
		bottomMs: 180,
		totalMs: 450,
		flashMs: 200
	});
});

test('enqueueGlyph queues ordered updates and deduplicates trailing value', () => {
	const queue = [];
	enqueueGlyph(queue, 'b', 'A');
	enqueueGlyph(queue, 'c', 'A');
	enqueueGlyph(queue, 'c', 'A');
	assert.deepEqual(queue, ['B', 'C']);
});

test('shouldFlash true only for reduced-motion path', () => {
	assert.equal(shouldFlash(true), true);
	assert.equal(shouldFlash(false), false);
});
