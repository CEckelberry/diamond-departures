<script lang="ts">
	import { onMount, untrack } from "svelte";
	import { normalizeGlyph, GLYPHS } from "./animation.mjs";
	import { noteFlapFlip } from "$lib/audio/flap";
	import { einkStore } from "$lib/stores/eink";

	let { value, width = 28, height = 36, onFlip = () => {}, staggerIndex = 0 } = $props();

	const targetGlyph = $derived(normalizeGlyph(value));
	let currentGlyph = $state(" ");
	let nextGlyph = $state(" ");
	let isFlipping = $state(false);

	const timingSkew = 0.88 + (Math.random() * 0.24);
	const flipDuration = $derived(
		($einkStore === 'aesthetic' ? 350 :
		 $einkStore === 'faithful' ? 1 : 70) * timingSkew
	);
	const halfHeight = Math.floor(height / 2);

	// Single queue + timer; no CSS animationend dependency (avoids animation-restart batching bug).
	let queue: string[] = [];
	let disposed = false;
	let flipTimer: ReturnType<typeof setTimeout> | null = null;
	let introTimer: ReturnType<typeof setTimeout> | null = null;

	function scheduleNextFlip() {
		if (disposed || queue.length === 0) { isFlipping = false; return; }
		nextGlyph = queue.shift()!;
		isFlipping = true;
		onFlip();
		noteFlapFlip();
		flipTimer = setTimeout(() => {
			currentGlyph = nextGlyph;
			isFlipping = false; // must go false so Svelte removes .flipping before next flip restarts animation
			setTimeout(scheduleNextFlip, 0);
		}, flipDuration);
	}

	onMount(() => {
		if (targetGlyph === " ") return () => { disposed = true; };

		introTimer = setTimeout(() => {
			if (disposed) return;
			const offset = (staggerIndex % 4) + 2; // 2–5 flips per cell (was 5–24)
			const startIdx = (GLYPHS.indexOf(targetGlyph) - offset + GLYPHS.length) % GLYPHS.length;
			currentGlyph = GLYPHS[startIdx];

			let i = (startIdx + 1) % GLYPHS.length;
			const targetIdx = GLYPHS.indexOf(targetGlyph);
			while (true) {
				queue.push(GLYPHS[i]);
				if (i === targetIdx) break;
				i = (i + 1) % GLYPHS.length;
			}
			scheduleNextFlip();
		}, staggerIndex * 2); // 2ms stagger (was 6ms)

		return () => {
			disposed = true;
			if (flipTimer) clearTimeout(flipTimer);
			if (introTimer) clearTimeout(introTimer);
		};
	});

	// Handle live value changes after initial mount.
	let mounted = false;
	$effect(() => {
		const target = targetGlyph;
		if (!mounted) { mounted = true; return; }
		untrack(() => {
			const tail = queue.length > 0 ? queue[queue.length - 1] : currentGlyph;
			const startIndex = Math.max(0, GLYPHS.indexOf(tail));
			const targetIndex = Math.max(0, GLYPHS.indexOf(target));
			if (startIndex === targetIndex) return;
			let i = (startIndex + 1) % GLYPHS.length;
			while (true) {
				queue.push(GLYPHS[i]);
				if (i === targetIndex) break;
				i = (i + 1) % GLYPHS.length;
			}
			if (!isFlipping) scheduleNextFlip();
		});
	});
</script>

<div
	class="cell"
	class:flipping={isFlipping}
	style="--cell-width:{width}px;--cell-height:{height}px;--half-height:{halfHeight}px;--flip-duration:{flipDuration}ms;"
	aria-label={`split-flap-cell-${currentGlyph}`}
>
	<!-- Background faces (Static) -->
	<div class="face top-bg">
		<span class="glyph">{nextGlyph}</span>
		<div class="shadow-top"></div>
	</div>
	<div class="face bottom-bg">
		<span class="glyph">{currentGlyph}</span>
		<div class="shadow-bottom"></div>
	</div>
	
	<!-- Animated flap -->
	<!-- The flap is always in the DOM but only animates when .flipping is applied -->
	<div class="flap">
		<div class="face flap-front">
			<span class="glyph">{currentGlyph}</span>
			<div class="shadow-flap-front"></div>
		</div>
		<div class="face flap-back">
			<span class="glyph">{nextGlyph}</span>
			<div class="shadow-flap-back"></div>
		</div>
	</div>
	
	<div class="hairline"></div>
</div>

<style>
	.cell {
		position: relative;
		display: inline-block;
		width: var(--cell-width);
		height: var(--cell-height);
		border-radius: 4px;
		background: var(--cell-bg);
		box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--cell-edge) 60%, transparent), 0 2px 4px rgba(0,0,0,0.5);
		font-family: "JetBrains Mono", monospace;
		font-weight: 700;
		color: var(--cell-text);
		perspective: 400px;
		/* Force hardware acceleration */
		transform: translateZ(0);
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
		backface-visibility: hidden;
		transform: translateZ(0);
	}

	.glyph {
		position: absolute;
		left: 50%;
		transform: translateX(-50%);
		height: var(--cell-height);
		/* Nudge text down slightly so its optical baseline centers on the mechanical seam */
		top: 1px;
		font-size: calc(var(--cell-height) * 0.72);
		line-height: 1;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.top-bg {
		top: 0;
		align-items: flex-start;
		background: linear-gradient(to bottom, color-mix(in oklab, var(--cell-bg) 85%, white), var(--cell-bg));
	}
	.top-bg .glyph { top: 0; bottom: auto; }

	.bottom-bg {
		bottom: 0;
		align-items: flex-end;
		background: linear-gradient(to top, color-mix(in oklab, var(--cell-bg) 88%, black), var(--cell-bg));
	}
	.bottom-bg .glyph { bottom: 0; top: auto; }

	.flap {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: var(--half-height);
		transform-origin: bottom center;
		transform-style: preserve-3d;
		z-index: 10;
		/* Reset state when not flipping */
		transform: rotateX(0deg);
	}

	.flipping .flap {
		/* ease-in mimics gravity on a falling mechanical flap */
		animation: flip var(--flip-duration) cubic-bezier(0.4, 0, 1, 1) forwards;
	}

	.flap-front, .flap-back {
		position: absolute;
		left: 0;
		top: 0;
		width: 100%;
		height: 100%;
		backface-visibility: hidden;
	}

	.flap-front {
		align-items: flex-start;
		background: linear-gradient(to bottom, color-mix(in oklab, var(--cell-bg) 85%, white), var(--cell-bg));
	}
	.flap-front .glyph { top: 0; bottom: auto; }

	.flap-back {
		align-items: flex-end;
		background: linear-gradient(to top, color-mix(in oklab, var(--cell-bg) 88%, black), var(--cell-bg));
		transform: rotateX(180deg);
	}
	.flap-back .glyph { bottom: 0; top: auto; }

	.hairline {
		position: absolute;
		top: calc(50% - 0.5px);
		left: 0;
		width: 100%;
		height: 1px;
		background: color-mix(in oklab, var(--cell-edge) 80%, black);
		z-index: 20;
	}

	/* LIGHTING EFFECTS */
	.shadow-top, .shadow-bottom, .shadow-flap-front, .shadow-flap-back {
		position: absolute;
		inset: 0;
		pointer-events: none;
		opacity: 0;
	}

	.flipping .bottom-bg .shadow-bottom {
		background: linear-gradient(to bottom, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 100%);
		animation: shadow-in var(--flip-duration) linear forwards;
	}

	.flipping .top-bg .shadow-top {
		background: linear-gradient(to bottom, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 100%);
		animation: shadow-out var(--flip-duration) linear forwards;
	}

	.flipping .flap-front .shadow-flap-front {
		background: linear-gradient(to bottom, rgba(0,0,0,0) 0%, rgba(0,0,0,0.8) 100%);
		animation: shadow-in var(--flip-duration) linear forwards;
	}

	.flipping .flap-back .shadow-flap-back {
		background: linear-gradient(to bottom, rgba(0,0,0,0) 0%, rgba(0,0,0,0.8) 100%);
		animation: shadow-out var(--flip-duration) linear forwards;
	}

	@keyframes flip {
		0% { transform: rotateX(0deg); }
		100% { transform: rotateX(-180deg); }
	}

	@keyframes shadow-in {
		0% { opacity: 0; }
		100% { opacity: 1; }
	}

	@keyframes shadow-out {
		0% { opacity: 1; }
		100% { opacity: 0; }
	}

	@media (prefers-reduced-motion: reduce) {
		.flipping .flap, .flipping .shadow-top, .flipping .shadow-bottom, .flipping .shadow-flap-front, .flipping .shadow-flap-back { 
			animation: none !important; 
		}
	}
</style>
