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

	const rowAriaLabel = $derived(
		`rank ${row.rank.trim()}, ${row.player}, ${row.team}, ${row.position}, stat ${row.stat}`
	);

	function handleSelect() {
		onselect?.(row.playerId);
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			handleSelect();
		}
	}
</script>

<div
	class="board-row"
	role="button"
	tabindex="0"
	aria-label={rowAriaLabel}
	onclick={handleSelect}
	onkeydown={handleKeydown}
>
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
		min-height: 44px;
		align-items: center;
		gap: 0.45rem;
		padding: 0.1rem 0.15rem;
		cursor: pointer;
		border-radius: 0.35rem;
	}

	.board-row:focus-visible {
		outline: 2px solid color-mix(in oklab, var(--cell-text) 70%, white);
		outline-offset: 2px;
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
			grid-template-columns: 1fr;
			gap: 0.25rem;
			padding: 0.5rem;
			background: color-mix(in oklab, var(--chrome-bg) 82%, black);
			border: 1px solid color-mix(in oklab, var(--chrome-text) 16%, transparent);
		}

		.rank,
		.team,
		.position,
		.stat {
			font-size: 0.7rem;
		}
	}
</style>
