<script lang="ts">
	import Word from '$lib/components/flap/Word.svelte';
	import type { BoardRow } from './types';

	let {
		row,
		onselect
	}: {
		row: BoardRow & { justQualified?: boolean };
		onselect?: (playerId: number) => void;
	} = $props();

	function handleSelect() {
		onselect?.(row.playerId);
	}
</script>

<div class="board-row" role="row" onclick={handleSelect}>
	<div class="cell rank" role="gridcell">
		<Word value={row.rank} width={3} cellWidth={20} cellHeight={30} />
	</div>
	<div class="cell player" role="gridcell">
		<Word value={row.player} width={18} cellWidth={20} cellHeight={30} />
		{#if row.justQualified}
			<span class="just-qualified-badge" style:--badge-fade-duration="24h">(just qualified)</span>
		{/if}
	</div>
	<div class="cell team" role="gridcell">
		<Word value={row.team} width={4} cellWidth={20} cellHeight={30} />
	</div>
	<div class="cell position" role="gridcell">
		<Word value={row.position} width={4} cellWidth={20} cellHeight={30} />
	</div>
	<div class="cell stat" role="gridcell">
		<Word value={row.stat} width={6} cellWidth={20} cellHeight={30} />
	</div>
</div>

<style>
	.board-row {
		display: grid;
		grid-template-columns: 3.5rem 20rem 6rem 6rem 8rem;
		height: 36px;
		align-items: center;
		gap: 0.45rem;
	}

	.cell {
		overflow: hidden;
	}

	.player {
		display: flex;
		align-items: center;
		gap: 0.28rem;
	}

	.just-qualified-badge {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.58rem;
		text-transform: lowercase;
		opacity: 0.95;
		animation: badge-fade var(--badge-fade-duration, 24h) linear forwards;
	}

	@keyframes badge-fade {
		0% {
			opacity: 0.95;
		}
		100% {
			opacity: 0.05;
		}
	}

	@media (max-width: 920px) {
		.board-row {
			grid-template-columns: 2.8rem 15rem 4.2rem 4.2rem 6.2rem;
			gap: 0.35rem;
		}
	}
</style>
