<script lang="ts">
	import { onMount, untrack } from "svelte";
	import { normalizeGlyph, GLYPHS } from "./animation.mjs";
	import { noteFlapFlip } from "$lib/audio/flap";
	import { einkStore } from "$lib/stores/eink";
	import { anim } from "$lib/stores/board.svelte";

	let { value, width = 28, height = 36, onFlip = () => {}, staggerIndex = 0, colIndex = 0, rowIndex = 0 } = $props();

	const targetGlyph = $derived(normalizeGlyph(value));
	const halfHeight = Math.floor(height / 2);
	const timingSkew = 0.88 + (Math.random() * 0.24);
	// Reactive so eink-mode changes take effect on next flip without remounting
	const baseDuration = $derived(
		($einkStore === 'aesthetic' ? 480 :
		 $einkStore === 'faithful' ? 1 : 400) * timingSkew
	);

	// Plain JS — no $state, so animation updates never touch Svelte's scheduler
	let currentChar = normalizeGlyph(value);
	let queue: string[] = [];
	let disposed = false;
	let isFlipping = false;
	let flipTimer: ReturnType<typeof setTimeout> | null = null;
	let introTimer: ReturnType<typeof setTimeout> | null = null;

	// DOM refs — animation writes textContent and class directly
	let cellEl: HTMLDivElement | undefined;
	let topBgRef: HTMLSpanElement | undefined;
	let botBgRef: HTMLSpanElement | undefined;
	let flapFRef: HTMLSpanElement | undefined;
	let flapBRef: HTMLSpanElement | undefined;

	function snapTo(ch: string) {
		currentChar = ch;
		if (!cellEl) return;
		topBgRef!.textContent = ch;
		botBgRef!.textContent = ch;
		flapFRef!.textContent = ch;
		cellEl.classList.remove('flipping');
		isFlipping = false;
	}

	function scheduleNextFlip() {
		if (disposed || !cellEl || queue.length === 0) { isFlipping = false; return; }
		const next = queue.shift()!;
		const dur = baseDuration; // reads current $derived value
		isFlipping = true;
		onFlip();
		noteFlapFlip();

		cellEl.style.setProperty('--flip-duration', `${dur}ms`);
		topBgRef!.textContent = next;
		flapFRef!.textContent = currentChar;
		flapBRef!.textContent = next;
		cellEl.classList.add('flipping');

		flipTimer = setTimeout(() => {
			if (disposed || !cellEl) return;
			// Update all faces before removing class so flap snaps to correct char
			botBgRef!.textContent = next;
			flapFRef!.textContent = next;
			cellEl.classList.remove('flipping');
			currentChar = next;
			isFlipping = false;
			requestAnimationFrame(() => { if (!disposed) scheduleNextFlip(); });
		}, dur);
	}

	onMount(() => {
		// Seed DOM text with initial value
		const init = normalizeGlyph(value);
		topBgRef!.textContent = init;
		botBgRef!.textContent = init;
		flapFRef!.textContent = init;
		flapBRef!.textContent = init;

		if (init === " " || anim.snap) return () => { disposed = true; };

		// 20% of cells do a settle flip on load for the "live board waking up" feel
		if (Math.random() >= 0.20) return () => { disposed = true; };

		const delay = anim.firstLoadDone
			? rowIndex * 40 + Math.random() * 150
			: Math.random() * 2000;
		introTimer = setTimeout(() => {
			if (disposed || anim.snap) return;
			const targetIdx = GLYPHS.indexOf(init);
			const startIdx = (targetIdx - 1 + GLYPHS.length) % GLYPHS.length;
			snapTo(GLYPHS[startIdx]);
			queue.push(init);
			scheduleNextFlip();
		}, delay);

		return () => {
			disposed = true;
			if (flipTimer) clearTimeout(flipTimer);
			if (introTimer) clearTimeout(introTimer);
		};
	});

	let mounted = false;
	let staggerTimer: ReturnType<typeof setTimeout> | null = null;
	$effect(() => {
		const target = targetGlyph; // sole reactive dependency
		if (!mounted) { mounted = true; return; }

		untrack(() => {
			if (anim.snap) {
				queue.length = 0;
				if (flipTimer) { clearTimeout(flipTimer); flipTimer = null; }
				snapTo(target);
				return;
			}

			// Early bail: already at target
			const tail = queue.length > 0 ? queue[queue.length - 1] : currentChar;
			if (tail === target) return;

			if (staggerTimer) clearTimeout(staggerTimer);
			staggerTimer = setTimeout(() => {
				if (disposed || anim.snap) return;
				if (Math.random() >= anim.density) { snapTo(target); return; }

				const t2 = queue.length > 0 ? queue[queue.length - 1] : currentChar;
				const si = Math.max(0, GLYPHS.indexOf(t2));
				const ti = Math.max(0, GLYPHS.indexOf(target));
				if (si === ti) return;
				const n = GLYPHS.length;
				const dist = (ti - si + n) % n;
				if (dist <= 3) {
					let i = (si + 1) % n;
					while (true) { queue.push(GLYPHS[i]); if (i === ti) break; i = (i + 1) % n; }
				} else {
					queue.push(
						GLYPHS[(si + Math.ceil(dist * 0.33)) % n],
						GLYPHS[(si + Math.ceil(dist * 0.67)) % n],
						GLYPHS[ti],
					);
				}
				if (!isFlipping) scheduleNextFlip();
			}, rowIndex * 22 + colIndex * 11);
		});
		return () => { if (staggerTimer !== null) { clearTimeout(staggerTimer); staggerTimer = null; } };
	});
</script>

<div
	bind:this={cellEl}
	class="cell"
	style="--cell-width:{width}px;--cell-height:{height}px;--half-height:{halfHeight}px;--flip-duration:{baseDuration}ms;"
	aria-label="split-flap-cell"
>
	<div class="face top-bg"><span class="glyph" bind:this={topBgRef}></span></div>
	<div class="face bottom-bg"><span class="glyph" bind:this={botBgRef}></span></div>
	<div class="flap">
		<div class="face flap-front"><span class="glyph" bind:this={flapFRef}></span></div>
		<div class="face flap-back"><span class="glyph" bind:this={flapBRef}></span></div>
	</div>
	
	<div class="hairline"></div>
</div>

<style>
	.cell {
		position: relative;
		display: inline-block;
		width: var(--cell-width);
		height: var(--cell-height);
		border-radius: 3px;
		background: var(--cell-bg);
		/* outline instead of box-shadow: avoids CPU repaint on class toggle */
		outline: 1px solid var(--cell-edge, rgba(255,255,255,0.15));
		font-family: "JetBrains Mono", monospace;
		font-weight: 700;
		color: var(--cell-text);
		/* No perspective at rest — only added via :global(.flipping) to avoid
		   maintaining 680 composited 3D contexts when nothing is animating */
		/* contain: layout style isolates reflow from display toggles inside the cell */
		contain: layout style;
	}

	/* 3D context only exists while a cell is actually flipping */
	:global(.flipping) {
		perspective: calc(var(--cell-height) * 1.8);
	}

	.face {
		position: absolute;
		left: 0;
		width: 100%;
		height: var(--half-height);
		overflow: hidden;
		display: flex;
		justify-content: center;
		background: var(--cell-bg);
		/* No backface-visibility here — these divs are never 3D-transformed */
	}

	/* Additive gradient overlays — no color-mix(), avoids per-repaint CPU cost */
	.top-bg::before, .flap-front::before {
		content: '';
		position: absolute;
		inset: 0;
		background: linear-gradient(to bottom, rgba(255,255,255,0.10) 0%, transparent 100%);
		pointer-events: none;
	}
	.bottom-bg::before, .flap-back::before {
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
		height: var(--cell-height);
		top: 1px;
		font-size: calc(var(--cell-height) * 0.72);
		line-height: 1;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.top-bg { top: 0; align-items: flex-start; }
	.top-bg .glyph { top: 0; bottom: auto; }

	.bottom-bg { bottom: 0; align-items: flex-end; }
	.bottom-bg .glyph { bottom: 0; top: auto; }

	.flap {
		position: absolute;
		top: 0; left: 0;
		width: 100%;
		height: var(--half-height);
		transform-origin: bottom center;
		/* No transform-style or will-change at rest */
		z-index: 10;
	}

	:global(.flipping) .flap {
		transform-style: preserve-3d;
		will-change: transform;
		animation: flip-card var(--flip-duration) linear forwards;
	}

	.flap-front {
		position: absolute;
		left: 0; top: 0;
		width: 100%; height: 100%;
		align-items: flex-start;
		/* No backface-visibility at rest — avoids composited layer promotion */
	}
	.flap-front .glyph { top: 0; bottom: auto; }

	/* backface-visibility added only when flipping — not needed at rest */
	:global(.flipping) .flap-front { backface-visibility: hidden; }

	/* Hidden at rest — display:none means no composited layer for a 3D-transformed element */
	.flap-back {
		display: none;
		position: absolute;
		left: 0; top: 0;
		width: 100%; height: 100%;
		align-items: flex-end;
		backface-visibility: hidden;
		transform: rotateX(180deg);
	}
	.flap-back .glyph { bottom: 0; top: auto; }

	:global(.flipping) .flap-back { display: flex; }

	/* 2px: top pixel = faint card-edge highlight, bottom pixel = shadow gap */
	.hairline {
		position: absolute;
		top: calc(50% - 1px);
		left: 0; width: 100%; height: 2px;
		background: linear-gradient(to bottom, rgba(255,255,255,0.22) 0%, rgba(0,0,0,0.75) 100%);
		z-index: 20;
		pointer-events: none;
	}

	/* Shadow handled by face gradients — no ::after animation avoids per-cell GPU layer during flip */

	/*
	 * Gravity fall + mechanical stop
	 * 0→55%:  free fall — starts immediately, builds naturally
	 * 55→80%: decelerating into the stop
	 * 80→89%: overshoot (mechanical slap, exaggerated for screen)
	 * 89→96%: damped bounce back
	 * 96→100%: final settle
	 */
	@keyframes flip-card {
		0%   { transform: rotateX(0deg);    animation-timing-function: cubic-bezier(0.35, 0, 0.95, 0.1); }
		55%  { transform: rotateX(-90deg);  animation-timing-function: cubic-bezier(0, 0.15, 0.4, 1); }
		80%  { transform: rotateX(-170deg); animation-timing-function: cubic-bezier(0.05, 0.8, 0.25, 1); }
		89%  { transform: rotateX(-205deg); animation-timing-function: cubic-bezier(0.6, 0, 0.85, 0.85); }
		96%  { transform: rotateX(-177deg); animation-timing-function: cubic-bezier(0.35, 0, 0.65, 1); }
		100% { transform: rotateX(-180deg); }
	}


	@media (prefers-reduced-motion: reduce) {
		.flipping .flap { animation: none !important; }
	}
</style>
