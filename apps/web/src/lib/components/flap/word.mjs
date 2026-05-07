import { normalizeGlyph } from './animation.mjs';

const NUMERIC_RE = /^[\d+\-.\s%]+$/;

/**
 * @param {string} value
 */
export function isNumericWord(value) {
	return NUMERIC_RE.test(value.trim());
}

/**
 * @param {string} value
 * @param {number} width
 */
export function buildCells(value, width) {
	const target = Math.max(1, width);
	const glyphs = Array.from(String(value ?? '').toUpperCase()).slice(0, target).map(normalizeGlyph);
	const padded = Array.from({ length: target }, () => ' ');
	const numeric = isNumericWord(value);

	if (numeric) {
		const start = target - glyphs.length;
		for (let i = 0; i < glyphs.length; i += 1) padded[start + i] = glyphs[i];
		return padded;
	}

	for (let i = 0; i < glyphs.length; i += 1) padded[i] = glyphs[i];
	return padded;
}

/**
 * @param {string[]} fromCells
 * @param {string[]} toCells
 */
export function diffCells(fromCells, toCells) {
	const changed = [];
	const width = Math.max(fromCells.length, toCells.length);
	for (let i = 0; i < width; i += 1) {
		if ((fromCells[i] ?? ' ') !== (toCells[i] ?? ' ')) changed.push(i);
	}
	return changed;
}
