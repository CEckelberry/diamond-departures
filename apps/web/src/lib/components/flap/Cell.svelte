<script lang="ts">
	import { onMount, untrack } from "svelte";
	import { normalizeGlyph, GLYPHS } from "./animation.mjs";
	import { noteFlapFlip } from "$lib/audio/flap";

	let { value, width = 28, height = 36, onFlip = () => {}, staggerIndex = 0 } = $props();

	const targetGlyph = $derived(normalizeGlyph(value));
	let currentGlyph = $state(" ");
	let nextGlyph = $state(" ");
	
	let isFlipping = $state(false);
	let queue: string[] = []; 
	let disposed = false;
	
	const timingSkew = 0.85 + (Math.random() * 0.3);
	const flipDuration = 80 * timingSkew; 
	const halfHeight = Math.floor(height / 2);

	onMount(() => {
		if (typeof window === "undefined") return;
		return () => { disposed = true; };
	});

	// React to value changes
	$effect(() => {
		const target = targetGlyph;
		
		untrack(() => {
			if (currentGlyph === target && queue.length === 0) return;
			
			// Always stagger updates to prevent main thread lockups when 600+ cells change at once (e.g. tab switches)
			const delay = staggerIndex * 2; // 2ms stagger = ~1.2s to start the last cell
			
			setTimeout(() => {
				if (disposed) return;
				
				let startIndex = GLYPHS.indexOf(currentGlyph);
				let targetIndex = GLYPHS.indexOf(target);
				if (startIndex === -1) startIndex = 0;
				if (targetIndex === -1) targetIndex = 0;
				
				if (queue.length > 0) {
					startIndex = GLYPHS.indexOf(queue[queue.length - 1]);
				}
				
				let dist = (targetIndex - startIndex + GLYPHS.length) % GLYPHS.length;
				
				if (dist > 2) {
					// Fast mechanical blur: jump straight to target with only 1 intermediate character
					const offset = ((staggerIndex * 7) % 17) + 1;
					const intermediateIdx = (startIndex + offset) % GLYPHS.length;
					queue.push(GLYPHS[intermediateIdx]);
					queue.push(target);
				} else {
					let i = (startIndex + 1) % GLYPHS.length;
					while (true) {
						queue.push(GLYPHS[i]);
						if (i === targetIndex) break;
						i = (i + 1) % GLYPHS.length;
					}
				}
				processQueue();
			}, delay);
		});
	});

	function processQueue() {
		if (isFlipping || disposed || queue.length === 0) return;
		
		nextGlyph = queue.shift()!;
		isFlipping = true;
		onFlip();
		noteFlapFlip();
	}

	function onAnimationEnd(event: AnimationEvent) {
		if (event.animationName !== 'flip') return;

		currentGlyph = nextGlyph;
		isFlipping = false;
		
		if (queue.length > 0) {
			setTimeout(processQueue, 2);
		}
	}
</script>

<div
	class="cell"
	class:flipping={isFlipping}
	style="--cell-width:{width}px;--cell-height:{height}px;--half-height:{halfHeight}px;--flip-duration:{flipDuration}ms;"
	aria-label={`split-flap-cell-${currentGlyph}`}
>
	<!-- Static Backgrounds -->
	<div class="face top-bg">
		<span class="glyph">{nextGlyph}</span>
	</div>
	<div class="face bottom-bg">
		<span class="glyph">{currentGlyph}</span>
	</div>
	
	<!-- Animated Flap -->
	<div class="flap" onanimationend={onAnimationEnd}>
		<div class="face flap-front">
			<span class="glyph">{currentGlyph}</span>
		</div>
		<div class="face flap-back">
			<span class="glyph">{nextGlyph}</span>
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
		/* Fixed centering: transform handles horizontal AND the 1px vertical mechanical nudge */
		transform: translate(-50%, 1px);
		height: var(--cell-height);
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
		display: none;
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: var(--half-height);
		transform-origin: bottom center;
		transform-style: preserve-3d;
		z-index: 10;
	}

	.flipping .flap {
		display: block;
		animation: flip var(--flip-duration) cubic-bezier(0.4, 0.0, 0.2, 1) forwards;
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

	.flipping .bottom-bg { animation: darken var(--flip-duration) ease-in forwards; }
	.flipping .top-bg { animation: lighten var(--flip-duration) ease-in forwards; }
	.flipping .flap-front { animation: darken var(--flip-duration) ease-in forwards; }
	.flipping .flap-back { animation: lighten var(--flip-duration) ease-in forwards; }

	@keyframes flip {
		0% { transform: rotateX(0deg); }
		100% { transform: rotateX(-180deg); }
	}
	@keyframes darken {
		0% { filter: brightness(1); }
		100% { filter: brightness(0.4); }
	}
	@keyframes lighten {
		0% { filter: brightness(0.4); }
		100% { filter: brightness(1); }
	}

	@media (prefers-reduced-motion: reduce) {
		.flipping .flap, .flipping .face { animation: none !important; }
	}
</style>
