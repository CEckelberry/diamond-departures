export const FLIP_TIMINGS = {
	topMs: 150,
	pauseMs: 120,
	bottomMs: 180,
	totalMs: 450,
	flashMs: 200
};

/**
 * @param {string | null | undefined} value
 */
export function normalizeGlyph(value) {
	return String(value ?? ' ').slice(0, 1).toUpperCase() || ' ';
}

/**
 * @param {string[]} queue
 * @param {string | null | undefined} nextValue
 * @param {string | null | undefined} currentValue
 */
export function enqueueGlyph(queue, nextValue, currentValue) {
	const next = normalizeGlyph(nextValue);
	const current = normalizeGlyph(currentValue);
	if (next === current) return;
	if (queue.length > 0 && queue[queue.length - 1] === next) return;
	queue.push(next);
}

/**
 * @param {boolean} reducedMotion
 */
export function shouldFlash(reducedMotion) {
	return Boolean(reducedMotion);
}

/**
 * @param {number} ms
 */
export function wait(ms) {
	return new Promise((resolve) => setTimeout(resolve, ms));
}
