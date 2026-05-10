<script lang="ts">
	import { onMount } from "svelte";
	import {
		FLIP_TIMINGS,
		enqueueGlyph,
		normalizeGlyph,
		shouldFlash,
		wait
	} from "./animation.mjs";
	import { noteFlapFlip } from "$lib/audio/flap";

	type CellProps = {
		value: string;
		width?: number;
		height?: number;
		onFlip?: () => void;
	};

	let { value, width = 28, height = 36, onFlip = () => {} }: CellProps = $props();

	const normalizedValue = $derived(normalizeGlyph(value));
	let glyph = $state(" ");
	let queue = $state<string[]>([]);
	let animating = $state(false);
	let phase = $state<"idle" | "top" | "pause" | "bottom">("idle");
	let flash = $state(false);
	let reducedMotion = $state(false);
	let disposed = false;

	const half = $derived(Math.floor(height / 2));
	const phaseClass = $derived(
		phase === "idle" ? "" : phase === "pause" ? "pause-phase" : `${phase}-phase`
	);

	onMount(() => {
		if (typeof window === "undefined") return;

		const media = window.matchMedia("(prefers-reduced-motion: reduce)");
		const update = () => {
			reducedMotion = media.matches;
		};
		update();
		media.addEventListener("change", update);

		return () => {
			disposed = true;
			media.removeEventListener("change", update);
		};
	});

	$effect(() => {
		enqueueGlyph(queue, normalizedValue, glyph);
		if (glyph === " " && queue.length === 1 && !animating) {
			glyph = queue.shift() ?? glyph;
			return;
		}
		void runQueue();
	});

	async function runQueue() {
		if (animating) return;
		animating = true;

		while (!disposed && queue.length > 0) {
			const nextGlyph = queue.shift();
			if (!nextGlyph) continue;

			if (shouldFlash(reducedMotion)) {
				glyph = nextGlyph;
				flash = true;
				await wait(FLIP_TIMINGS.flashMs);
				flash = false;
				continue;
			}

			onFlip();
			noteFlapFlip();
			phase = "top";
			await wait(FLIP_TIMINGS.topMs);
			phase = "pause";
			glyph = nextGlyph;
			await wait(FLIP_TIMINGS.pauseMs);
			phase = "bottom";
			await wait(FLIP_TIMINGS.bottomMs);
			phase = "idle";
		}

		animating = false;
	}
</script>

<div
	class={`cell ${phaseClass} ${flash ? "flash" : ""}`}
	style={`--cell-width:${width}px;--cell-height:${height}px;--half-height:${half}px;`}
	aria-label={`split-flap-cell-${glyph}`}
>
	<div class="face top" aria-hidden="true">
		<span class="glyph-container">{glyph}</span>
	</div>
	<div class="hairline" aria-hidden="true"></div>
	<div class="face bottom" aria-hidden="true">
		<span class="glyph-container">{glyph}</span>
	</div>
</div>

<style>
	.cell {
		position: relative;
		display: inline-block;
		width: var(--cell-width);
		height: var(--cell-height);
		border-radius: 3px;
		overflow: hidden;
		background: var(--cell-bg);
		box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--cell-edge) 60%, transparent);
		font-family: "JetBrains Mono", monospace;
		font-weight: 700;
		color: var(--cell-text);
	}

	.face {
		position: absolute;
		left: 0;
		width: 100%;
		height: var(--half-height);
		overflow: hidden;
		display: flex;
		justify-content: center;
		will-change: transform;
	}

	.glyph-container {
		position: absolute;
		left: 50%;
		/* Center horizontally */
		transform: translateX(-50%);
		/* Fix the height to the full cell height to ensure no clipping */
		height: var(--cell-height);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: calc(var(--cell-height) * 0.7);
		line-height: 1;
	}

	.top {
		top: 0;
		background: linear-gradient(
			to bottom,
			color-mix(in oklab, var(--cell-bg) 85%, white),
			var(--cell-bg)
		);
		transform-origin: center bottom;
		/* Align the top half of the character */
		align-items: flex-start;
	}

	.top .glyph-container {
		/* Position the container so its middle line is at the bottom of this face (the seam) */
		top: 0;
	}

	.bottom {
		bottom: 0;
		background: linear-gradient(
			to top,
			color-mix(in oklab, var(--cell-bg) 88%, black),
			var(--cell-bg)
		);
		transform-origin: center top;
		/* Align the bottom half of the character */
		align-items: flex-end;
	}

	.bottom .glyph-container {
		/* Position the container so its middle line is at the top of this face (the seam) */
		bottom: 0;
	}

	.hairline {
		position: absolute;
		top: calc(50% - 0.5px);
		left: 0;
		width: 100%;
		height: 1px;
		background: color-mix(in oklab, var(--cell-edge) 80%, black);
		z-index: 2;
	}

	.cell.top-phase .top {
		animation: flap-top var(--top-ms, 150ms) ease-in forwards;
	}

	.cell.pause-phase .hairline {
		background: color-mix(in oklab, var(--cell-text) 20%, var(--cell-edge));
	}

	.cell.bottom-phase .bottom {
		animation: flap-bottom var(--bottom-ms, 180ms) ease-out forwards;
	}

	.cell.flash {
		animation: reduced-flash 200ms ease-out;
	}

	@keyframes flap-top {
		0% {
			transform: rotateX(0deg);
			filter: brightness(1);
		}
		100% {
			transform: rotateX(-90deg);
			filter: brightness(0.82);
		}
	}

	@keyframes flap-bottom {
		0% {
			transform: rotateX(90deg);
			filter: brightness(0.7);
		}
		100% {
			transform: rotateX(0deg);
			filter: brightness(1);
		}
	}

	@keyframes reduced-flash {
		0% {
			box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--cell-edge) 60%, transparent);
		}
		50% {
			box-shadow:
				inset 0 0 0 1px color-mix(in oklab, var(--cell-text) 40%, var(--cell-edge)),
				0 0 0 1px color-mix(in oklab, var(--cell-text) 40%, transparent);
		}
		100% {
			box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--cell-edge) 60%, transparent);
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.cell.top-phase .top,
		.cell.bottom-phase .bottom {
			animation: none;
		}
	}
</style>
