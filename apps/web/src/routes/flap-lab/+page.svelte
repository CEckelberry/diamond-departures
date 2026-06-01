<script lang="ts">
	import { setContext } from 'svelte';
	import LabCell from '$lib/components/flap/LabCell.svelte';
	import type { LabConfig } from '$lib/components/flap/LabCell.svelte';

	const cfg: LabConfig = {
		flipDurationMs:  400,
		interFlipGapMs:  12,
		rowStaggerMs:    0,
		colStaggerMs:    0,
		timingSkewPct:   9,
		cellWidth:       160,
		cellHeight:      240,
		easingFn:        'cubic-bezier(0.55, 0, 0.85, 0)',
		alphabetSteps:   '3steps',
		shadowIntensity: 0.92,
	};
	setContext('labCfg', cfg);

	const CYCLE = ['A', 'M', '7', 'Z', '+', '1', 'B', '8', 'R', '5'];
	let step = $state(0);

	const char = $derived(CYCLE[step % CYCLE.length]);

	function trigger() { step++; }
</script>

<div class="theater">
	<LabCell value={char} rowIndex={0} colIndex={0} overrideWidth={160} overrideHeight={240} />
	<button class="trigger" onclick={trigger}>▶ FLIP</button>
</div>

<style>
	:global(html, body) {
		height: 100%;
		margin: 0;
		padding: 0;
		background: #000;
	}

	.theater {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100vh;
		gap: 3rem;
		background: #000;
	}

	.trigger {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.75rem;
		font-weight: 700;
		letter-spacing: .1em;
		text-transform: uppercase;
		padding: 0.5rem 1.5rem;
		border-radius: 0.35rem;
		border: 1px solid rgba(255, 255, 255, 0.15);
		background: transparent;
		color: rgba(255, 255, 255, 0.4);
		cursor: pointer;
		transition: color 0.15s, border-color 0.15s;
	}

	.trigger:hover {
		color: rgba(255, 255, 255, 0.75);
		border-color: rgba(255, 255, 255, 0.35);
	}

	.trigger:active {
		color: white;
		border-color: rgba(255, 255, 255, 0.6);
	}
</style>
