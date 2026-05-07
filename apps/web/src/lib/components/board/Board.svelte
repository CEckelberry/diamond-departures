<script lang="ts">
	import Row from './Row.svelte';
	import type { BoardRow } from './types';

	let { rows = [] }: { rows?: BoardRow[] } = $props();

	const placeholderRows = $derived(
		rows.length > 0
			? rows
			: Array.from({ length: 100 }, (_, index) => ({
					rank: String(index + 1).padStart(3, ' '),
					player: `PLAYER ${String(index + 1).padStart(2, '0')}`,
					team: ['ATL', 'LAD', 'NYY', 'SEA', 'SDP'][index % 5],
					position: ['SS', 'OF', '1B', 'SP', 'C'][index % 5],
					stat: (150 - index / 2).toFixed(1)
				}))
	);
</script>

<section class="board" aria-label="leaderboard board">
	<div class="board-header-row" role="row">
		<span>RK</span>
		<span>PLAYER</span>
		<span>TEAM</span>
		<span>POS</span>
		<span>STAT</span>
	</div>
	<div class="board-body" role="rowgroup">
		{#each placeholderRows as row, index (index)}
			<Row {row} />
		{/each}
	</div>
</section>

<style>
	.board {
		border-radius: 0.6rem;
		padding: 0.7rem;
		background: color-mix(in oklab, var(--board-bg) 92%, black);
		border: 1px solid color-mix(in oklab, var(--chrome-text) 18%, transparent);
	}

	.board-header-row {
		display: grid;
		grid-template-columns: 3.5rem 20rem 6rem 6rem 8rem;
		gap: 0.45rem;
		padding-bottom: 0.5rem;
		margin-bottom: 0.45rem;
		border-bottom: 1px solid color-mix(in oklab, var(--chrome-text) 14%, transparent);
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.67rem;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: color-mix(in oklab, var(--chrome-text) 72%, transparent);
	}

	.board-body {
		display: grid;
		gap: 0.2rem;
		max-height: min(72vh, 2300px);
		overflow: auto;
	}

	@media (max-width: 920px) {
		.board-header-row {
			grid-template-columns: 2.8rem 15rem 4.2rem 4.2rem 6.2rem;
			gap: 0.35rem;
		}
	}
</style>
