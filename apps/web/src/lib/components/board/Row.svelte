<script lang="ts">
	import Word from '$lib/components/flap/Word.svelte';
	import type { BoardRow } from './types';

	let {
		row,
		rowIndex = 0,
		sort = '',
		statCols = [],
		onselect
	}: {
		row: BoardRow;
		rowIndex?: number;
		sort?: string;
		statCols?: string[];
		onselect?: (playerId: number) => void;
	} = $props();

	// Integer stats: displayed as whole numbers, fit in 3 chars
	const INTEGER_STATS = new Set(['HR', 'RBI', 'SB', 'K', 'W', 'L', 'SV', 'G', 'GS', 'wRC+', 'OPS+']);

	function statWordWidth(name: string): number {
		return INTEGER_STATS.has(name) ? 3 : 5;
	}

	function formatStat(name: string, val: number | undefined): string {
		if (val === undefined || val === null) return '     ';
		if (INTEGER_STATS.has(name)) return String(Math.round(val));
		// Rate stats: .XXX, no leading zero (always between 0 and 1)
		if (['AVG', 'OBP', 'SLG', 'BABIP', 'ISO', 'wOBA'].includes(name)) return val.toFixed(3).replace(/^0/, '');
		// Percentage stats: stored as 0–1 decimal, displayed as "X.X%"
		if (['BB%', 'K%', 'K-BB%'].includes(name)) return (val * 100).toFixed(1) + '%';
		// OPS can exceed 1.0 → keep leading zero
		if (name === 'OPS') return val.toFixed(3);
		if (['ERA', 'FIP', 'xFIP', 'WHIP', 'K/9', 'BB/9'].includes(name)) return val.toFixed(2);
		return val < 10 ? val.toFixed(3) : String(Math.round(val));
	}

	const rowAriaLabel = $derived(
		`rank ${row.rank.trim()}, ${row.player}, ${row.team}, ${row.position}, stat ${row.stat}`
	);

	function handleClick() {
		onselect?.(row.playerId);
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			onselect?.(row.playerId);
		}
	}
</script>

<div
	class="board-row"
	class:just-qualified={row.justQualified}
	role="button"
	tabindex="0"
	aria-label={rowAriaLabel}
	onclick={handleClick}
	onkeydown={handleKeydown}
>
	<div class="cell"><Word value={row.rank} width={3} cellWidth={16} cellHeight={26} {rowIndex} baseColIndex={0} /></div>
	<div class="cell player">
		<Word value={row.player} width={Math.min(Math.max(1, row.player.trim().length), 18)} cellWidth={16} cellHeight={26} {rowIndex} baseColIndex={3} />
		{#if row.justQualified}
			<span class="just-qualified-badge" style="--badge-fade-duration: 86400s">(just qualified)</span>
		{/if}
	</div>
	<div class="cell"><Word value={row.team} width={3} cellWidth={16} cellHeight={26} {rowIndex} baseColIndex={21} /></div>
	<div class="cell"><Word value={row.position} width={2} cellWidth={16} cellHeight={26} {rowIndex} baseColIndex={24} /></div>
	{#key sort}
		{#each statCols as statName, colIdx}
			<div class="cell stat" class:stat-active={statName === sort}>
				<Word
					value={formatStat(statName, row.stats[statName])}
					width={statWordWidth(statName)} cellWidth={16} cellHeight={26}
					{rowIndex}
					baseColIndex={26 + colIdx * 5}
				/>
			</div>
		{/each}
	{/key}
</div>

<style>
	.board-row {
		display: grid;
		grid-template-columns: 3.5rem 21rem 5rem 4rem repeat(7, minmax(5rem, 1fr));
		height: 36px;
		align-items: center;
		gap: 0.6rem;
		padding: 0.1rem 0.2rem;
		min-height: 44px;
		cursor: pointer;
		border-radius: 0.25rem;
		transition: background 120ms ease;
	}

	.board-row:hover,
	.board-row:focus-visible {
		background: color-mix(in oklab, var(--cell-bg) 10%, transparent);
		outline: 1px solid color-mix(in oklab, var(--cell-text) 30%, transparent);
	}

	.cell {
		display: flex;
		align-items: center;
		overflow: hidden;
		position: relative;
	}

	.cell.stat {
		justify-content: center;
	}

	.player {
		padding-left: 0.5rem;
		padding-right: 1.5rem;
		gap: 0.4rem;
	}

	.stat-active {
		color: #fbbf24;
	}

	/* Overlay sits above Cell internals (hairline z-index:20) to tint the whole column */
	.stat-active::after {
		content: '';
		position: absolute;
		inset: 0;
		background: rgba(251, 191, 36, 0.09);
		pointer-events: none;
		z-index: 25;
		border-radius: 0.2rem;
	}

	.just-qualified-badge {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.55rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: var(--cell-text);
		opacity: 1;
		white-space: nowrap;
		animation: badge-fade var(--badge-fade-duration, 86400s) linear 0s 1 forwards;
	}

	@keyframes badge-fade {
		0% { opacity: 1; }
		90% { opacity: 1; }
		100% { opacity: 0; }
	}

	@media (max-width: 920px) {
		.board-row {
			grid-template-columns: 1fr;
			height: auto;
		}

		.cell:not(.player):not(.stat) {
			display: none;
		}
	}
</style>
