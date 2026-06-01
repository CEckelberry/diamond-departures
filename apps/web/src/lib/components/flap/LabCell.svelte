<script lang="ts">
	import { onMount, untrack, getContext } from 'svelte';
	import { normalizeGlyph, GLYPHS } from './animation.mjs';

	export interface LabConfig {
		flipDurationMs: number;
		interFlipGapMs: number;
		rowStaggerMs: number;
		colStaggerMs: number;
		timingSkewPct: number;
		cellWidth: number;
		cellHeight: number;
		easingFn: string;
		alphabetSteps: 'direct' | '3steps' | 'full';
		shadowIntensity: number;
	}

	let {
		value = ' ',
		rowIndex = 0,
		colIndex = 0,
		overrideWidth = undefined as number | undefined,
		overrideHeight = undefined as number | undefined,
	} = $props();

	const cfg = getContext<LabConfig>('labCfg');

	// ── Stable per-cell random for timing skew ────────────────────────────
	const cellRng = Math.random() * 2 - 1; // -1..1, fixed at cell creation

	// ── DOM refs — animation drives these directly, bypassing Svelte state ─
	let cellEl: HTMLDivElement | undefined;
	let topBgGlyph: HTMLSpanElement | undefined;
	let botBgGlyph: HTMLSpanElement | undefined;
	let flapFrontGlyph: HTMLSpanElement | undefined;
	let flapBackGlyph: HTMLSpanElement | undefined;

	// Plain JS variables (not $state) so updates don't trigger Svelte scheduler
	let currentChar = normalizeGlyph(value);
	let queue: string[] = [];
	let isFlipping = false;
	let dead = false;
	let flipTimer: ReturnType<typeof setTimeout> | null = null;
	let staggerTimer: ReturnType<typeof setTimeout> | null = null;

	function buildQueue(from: string, to: string): string[] {
		const fi = Math.max(0, GLYPHS.indexOf(from));
		const ti = Math.max(0, GLYPHS.indexOf(to));
		if (fi === ti) return [];
		const n = GLYPHS.length;
		const dist = (ti - fi + n) % n;

		if (cfg.alphabetSteps === 'direct') return [GLYPHS[ti]];

		if (cfg.alphabetSteps === 'full') {
			const s: string[] = [];
			let i = (fi + 1) % n;
			for (;;) { s.push(GLYPHS[i]); if (i === ti) break; i = (i + 1) % n; }
			return s;
		}

		// '3steps': max 2 intermediates + target so any cell settles in ≤3 flips
		if (dist <= 2) {
			const s: string[] = [];
			let i = (fi + 1) % n;
			for (;;) { s.push(GLYPHS[i]); if (i === ti) break; i = (i + 1) % n; }
			return s;
		}
		if (dist <= 6) {
			return [GLYPHS[(fi + Math.ceil(dist * 0.5)) % n], GLYPHS[ti]];
		}
		return [
			GLYPHS[(fi + Math.ceil(dist * 0.33)) % n],
			GLYPHS[(fi + Math.ceil(dist * 0.67)) % n],
			GLYPHS[ti],
		];
	}

	function advance() {
		if (dead || !cellEl || queue.length === 0) { isFlipping = false; return; }

		const next = queue.shift()!;
		isFlipping = true;

		const dur = Math.max(1, cfg.flipDurationMs * (1 + cellRng * cfg.timingSkewPct / 100));

		// ── Direct DOM — zero Svelte overhead ──────────────────────────────
		cellEl!.style.setProperty('--fd', `${dur}ms`); // per-cell skewed duration
		topBgGlyph!.textContent = next;                 // top half: upcoming char
		flapFrontGlyph!.textContent = currentChar;      // flap front: departing
		flapBackGlyph!.textContent = next;              // flap back: arriving
		cellEl!.classList.add('flipping');

		flipTimer = setTimeout(() => {
			if (dead || !cellEl) return;
			// Update all faces BEFORE removing class so the flap snaps to correct char
			botBgGlyph!.textContent = next;
			flapFrontGlyph!.textContent = next;   // flap front must match settled state
			cellEl.classList.remove('flipping');
			currentChar = next;
			isFlipping = false;

			if (queue.length > 0) {
				const gap = cfg.interFlipGapMs;
				if (gap > 0) {
					setTimeout(() => { if (!dead) advance(); }, gap);
				} else {
					requestAnimationFrame(() => { if (!dead) advance(); });
				}
			}
		}, dur);
	}

	// Only reactive to value prop changes — everything else is plain JS
	let mounted = false;
	$effect(() => {
		const target = normalizeGlyph(value); // sole reactive dependency
		if (!mounted) return;

		untrack(() => {
			// Early bail: if current state already matches target, skip timer entirely
			const tail = queue.length > 0 ? queue[queue.length - 1] : currentChar;
			if (tail === target) return;

			if (staggerTimer) { clearTimeout(staggerTimer); staggerTimer = null; }
			const delay = rowIndex * cfg.rowStaggerMs + colIndex * cfg.colStaggerMs;

			if (delay === 0) {
				// No stagger — fire immediately in next rAF to stay off the current microtask
				staggerTimer = setTimeout(() => {
					if (dead) return;
					const t2 = queue.length > 0 ? queue[queue.length - 1] : currentChar;
					const q = buildQueue(t2, target);
					if (!q.length) return;
					queue.push(...q);
					if (!isFlipping) advance();
				}, 0);
			} else {
				staggerTimer = setTimeout(() => {
					if (dead) return;
					const t2 = queue.length > 0 ? queue[queue.length - 1] : currentChar;
					const q = buildQueue(t2, target);
					if (!q.length) return;
					queue.push(...q);
					if (!isFlipping) advance();
				}, delay);
			}
		});

		return () => { if (staggerTimer) { clearTimeout(staggerTimer); staggerTimer = null; } };
	});

	onMount(() => {
		// Seed DOM text content once; animation owns it from here on
		const init = normalizeGlyph(value);
		topBgGlyph!.textContent = init;
		botBgGlyph!.textContent = init;
		flapFrontGlyph!.textContent = init;
		flapBackGlyph!.textContent = init;
		mounted = true;

		return () => {
			dead = true;
			if (flipTimer) clearTimeout(flipTimer);
			if (staggerTimer) clearTimeout(staggerTimer);
		};
	});

	// Derived only for CSS vars — doesn't drive any DOM
	const W = $derived(overrideWidth ?? cfg.cellWidth);
	const H = $derived(overrideHeight ?? cfg.cellHeight);
	const halfH = $derived(Math.floor(H / 2));
</script>

<!--
  Glyph spans start empty; onMount seeds them.
  All subsequent text updates go through direct DOM (advance()).
-->
<div
	bind:this={cellEl}
	class="cell"
	style="--w:{W}px;--h:{H}px;--hh:{halfH}px;--ease:{cfg.easingFn};--si:{cfg.shadowIntensity};"
>
	<div class="face top-bg"><span class="glyph" bind:this={topBgGlyph}></span></div>
	<div class="face bot-bg"><span class="glyph" bind:this={botBgGlyph}></span></div>
	<div class="flap">
		<div class="face flap-f"><span class="glyph" bind:this={flapFrontGlyph}></span></div>
		<div class="face flap-b"><span class="glyph" bind:this={flapBackGlyph}></span></div>
	</div>
	<div class="hairline"></div>
</div>

<style>
	/* ── Cell container ─────────────────────────────────────────────────── */
	.cell {
		position: relative;
		display: inline-block;
		width: var(--w);
		height: var(--h);
		border-radius: 3px;
		/* Use outline instead of box-shadow: outline doesn't trigger repaint on class change */
		outline: 1px solid var(--cell-edge, rgba(255,255,255,0.15));
		font-family: "JetBrains Mono", monospace;
		font-weight: 700;
		color: var(--cell-text);
		perspective: calc(var(--h) * 1.8);
	}

	/* ── Half-faces ─────────────────────────────────────────────────────── */
	.face {
		position: absolute;
		left: 0;
		width: 100%;
		height: var(--hh);
		overflow: hidden;
		display: flex;
		justify-content: center;
		/* Solid background: no color-mix(), avoids per-repaint CPU color interpolation */
		background: var(--cell-bg, #1a1a25);
		backface-visibility: hidden;
	}

	/* Top-half lightening — simulates overhead light on the card face */
	.top-bg::before, .flap-f::before {
		content: '';
		position: absolute;
		inset: 0;
		background: linear-gradient(to bottom, rgba(255,255,255,0.10) 0%, transparent 100%);
		pointer-events: none;
	}

	/* Bottom-half darkening — card in its own shadow */
	.bot-bg::before, .flap-b::before {
		content: '';
		position: absolute;
		inset: 0;
		background: linear-gradient(to top, rgba(0,0,0,0.30) 0%, transparent 100%);
		pointer-events: none;
	}

	.glyph {
		position: absolute;
		left: 50%;
		transform: translateX(-50%);
		height: var(--h);
		top: 1px;
		font-size: calc(var(--h) * 0.72);
		line-height: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		user-select: none;
	}

	.top-bg { top: 0; align-items: flex-start; }
	.top-bg .glyph { top: 0; }

	.bot-bg { bottom: 0; align-items: flex-end; }
	.bot-bg .glyph { bottom: 0; top: auto; }

	/* ── Animated flap ──────────────────────────────────────────────────── */
	.flap {
		position: absolute;
		top: 0; left: 0;
		width: 100%;
		height: var(--hh);
		transform-origin: bottom center;
		transform-style: preserve-3d;
		z-index: 10;
	}

	/* will-change only active while animating — avoids persistent layer cost */
	/* :global needed because .flipping is added via classList.add(), not a Svelte binding */
	:global(.flipping) .flap {
		will-change: transform;
		animation: flip-card linear forwards;
		/* Duration driven by JS via direct style on the element */
		animation-duration: var(--fd, 120ms);
	}

	.flap-f, .flap-b {
		position: absolute;
		left: 0; top: 0;
		width: 100%; height: 100%;
		backface-visibility: hidden;
	}

	.flap-f { align-items: flex-start; }
	.flap-f .glyph { top: 0; }

	.flap-b {
		align-items: flex-end;
		transform: rotateX(180deg);
	}
	.flap-b .glyph { bottom: 0; top: auto; }

	/* ── Hairline seam ──────────────────────────────────────────────────── */
	/* 2px: top pixel = faint white card-edge highlight, bottom pixel = shadow gap */
	.hairline {
		position: absolute;
		top: calc(50% - 1px);
		left: 0; width: 100%; height: 2px;
		background: linear-gradient(to bottom, rgba(255,255,255,0.22) 0%, rgba(0,0,0,0.75) 100%);
		z-index: 20;
		pointer-events: none;
	}

	/* ── Shadow: single ::after overlay instead of 4 animated divs ─────── */
	/* Halves shadow animation DOM cost from 4 elements → 1 pseudo-element  */
	.cell::after {
		content: '';
		position: absolute;
		inset: 0;
		background: linear-gradient(
			to bottom,
			rgba(0,0,0,0.55) 0%,
			transparent      45%,
			transparent      55%,
			rgba(0,0,0,0.35) 100%
		);
		opacity: 0;
		pointer-events: none;
		z-index: 15;
		border-radius: inherit;
	}

	:global(.flipping)::after {
		/* Shadow intensity respects --si variable */
		animation: cell-shadow linear forwards;
		animation-duration: var(--fd, 120ms);
		opacity: var(--si, 0.8);
	}

	/* ── Keyframes ──────────────────────────────────────────────────────── */

	/*
	 * flip-card: gravity fall with mechanical stop
	 *   0%→52%  : free fall — steep ease-in (near-zero velocity at release, slams hard)
	 *   52%→80% : post-edge deceleration into the stop
	 *   80%→90% : overshoot (mechanical slap past 180°)
	 *   90%→96% : bounce back (damped, quick)
	 *   96%→100%: final settle
	 */
	@keyframes flip-card {
		/* Gravity: starts moving immediately, builds naturally like a released flap */
		0%   { transform: rotateX(0deg);    animation-timing-function: cubic-bezier(0.35, 0, 0.95, 0.1); }
		/* Edge-on: maximum velocity */
		55%  { transform: rotateX(-90deg);  animation-timing-function: cubic-bezier(0, 0.15, 0.4, 1); }
		/* Decelerating into the stop */
		80%  { transform: rotateX(-170deg); animation-timing-function: cubic-bezier(0.05, 0.8, 0.25, 1); }
		/* Mechanical slap — exaggerated for screen */
		89%  { transform: rotateX(-205deg); animation-timing-function: cubic-bezier(0.6, 0, 0.85, 0.85); }
		/* Damped bounce back */
		96%  { transform: rotateX(-177deg); animation-timing-function: cubic-bezier(0.35, 0, 0.65, 1); }
		100% { transform: rotateX(-180deg); }
	}

	/* Shadow breathes in for first half, out for second */
	@keyframes cell-shadow {
		0%   { opacity: 0; }
		40%  { opacity: var(--si, 0.8); }
		100% { opacity: 0; }
	}

	@media (prefers-reduced-motion: reduce) {
		.flipping .flap, .flipping::after { animation: none !important; }
	}
</style>
