export const GLYPHS = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-+%+";

export const FLIP_TIMINGS = {
	topMs: 150,
	pauseMs: 120,
	bottomMs: 180,
	totalMs: 450,
	flashMs: 200
};

export function normalizeGlyph(value) {
	const char = String(value ?? " ").slice(0, 1).toUpperCase() || " ";
	return GLYPHS.includes(char) ? char : " ";
}

/**
 * Push current glyph to queue if not already the trailing item.
 * Deduplicates: if the last item in queue already equals normalised currentVal, skip.
 */
export function enqueueGlyph(queue, currentVal, targetVal) {
	const glyph = normalizeGlyph(currentVal);
	if (queue.length > 0 && queue[queue.length - 1] === glyph) return;
	queue.push(glyph);
}

/** Returns true when a reduced-motion flash is needed instead of a flip. */
export function shouldFlash(reducedMotion) {
	return Boolean(reducedMotion);
}
