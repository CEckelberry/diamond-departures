<script lang="ts">
	import Word from "$lib/components/flap/Word.svelte";
	import type { BoardRow } from "./types";
	import { page } from "$app/stores";

	let {
		row,
		onselect,
		boardStyle = "sabermetric"
	}: {
		row: BoardRow & { justQualified?: boolean };
		onselect?: (playerId: number) => void;
		boardStyle?: string;
	} = $props();

	const isPitcher = $derived(row.position === "SP" || row.position === "RP");
	const extraStatKeys = $derived((() => {
		if (isPitcher) {
			return boardStyle === "sabermetric" 
				? ["K/9", "BB/9", "FIP", "xFIP", "WAR"]
				: ["W", "L", "K", "ERA", "WHIP"];
		}
		return boardStyle === "sabermetric"
			? ["wRC+", "OPS+", "WAR", "DRS", "xwOBA"]
			: ["AVG", "HR", "RBI", "SB", "SLG"];
	})());

	function formatStat(key: string, val: number | undefined): string {
		if (val === undefined) return "---";
		
		if (["wRC+", "OPS+", "HR", "RBI", "SB", "W", "L", "K", "DRS", "H"].includes(key)) {
			return String(Math.round(val));
		}
		
		if (["AVG", "SLG", "OBP", "xwOBA"].includes(key)) {
			return val.toFixed(3).replace(/^0/, "");
		}
		
		if (["ERA", "WHIP", "FIP", "xFIP", "K/9", "BB/9", "WAR"].includes(key)) {
			return val.toFixed(2);
		}

		if (key === "OPS") {
			return val.toFixed(3).replace(/^0/, "");
		}
		
		return String(val);
	}

	const rowAriaLabel = $derived(
		`rank ${row.rank.trim()}, ${row.player}, ${row.team}, ${row.position}, stat ${row.stat}`
	);

	function handleSelect() {
		onselect?.(row.playerId);
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === "Enter" || event.key === " ") {
			event.preventDefault();
			handleSelect();
		}
	}
</script>

<div
	class="board-row"
	role="button"
	tabindex="0"
	onclick={handleSelect}
	onkeydown={handleKeydown}
>
	<div class="cell rank" role="gridcell">
		<Word value={row.rank} width={3} cellWidth={16} cellHeight={26} />
	</div>
	<div class="cell player" role="gridcell">
		<Word value={row.player} width={18} cellWidth={16} cellHeight={26} />
		{#if row.justQualified}
			<span class="just-qualified-badge">(new)</span>
		{/if}
	</div>
	<div class="cell team" role="gridcell">
		<Word value={row.team} width={3} cellWidth={16} cellHeight={26} />
	</div>
	<div class="cell position" role="gridcell">
		<Word value={row.position} width={2} cellWidth={16} cellHeight={26} />
	</div>
	{#each extraStatKeys as key}
		<div class="cell extra-stat" role="gridcell">
			<Word value={formatStat(key, row.stats[key])} width={key === 'OPS' ? 5 : 4} cellWidth={16} cellHeight={26} />
		</div>
	{/each}
	<div class="cell stat highlight-stat" role="gridcell">
		<Word value={formatStat($page.url.searchParams.get("sort") || (isPitcher ? "ERA" : "wRC+"), Number(row.stat))} width={5} cellWidth={16} cellHeight={26} />
	</div>
</div>

<style>
	.board-row {
		display: grid;
		grid-template-columns: 80px 1fr 100px 80px repeat(5, 100px) 130px;
		height: 32px;
		min-height: 38px;
		align-items: center;
		gap: 0.4rem;
		padding: 0.1rem 0.2rem;
		cursor: pointer;
		border-radius: 0.3rem;
		transition: background 150ms ease;
	}

	.board-row:hover {
		background: color-mix(in oklab, var(--chrome-bg) 60%, transparent);
	}

	.cell {
		display: flex;
		align-items: center;
		overflow: hidden;
	}

	.rank {
		padding-left: 0.4rem;
	}

	.player {
		padding-left: 1.2rem;
		gap: 0.4rem;
	}

	.just-qualified-badge {
		font-family: "JetBrains Mono", monospace;
		font-size: 0.5rem;
		text-transform: uppercase;
		color: var(--mlb-blue);
		font-weight: 700;
	}

	.stat {
		justify-content: flex-end;
		padding-right: 1.2rem;
	}

	.highlight-stat :global(.cell) {
		--cell-text: #ffd700; /* Gold accent */
	}

	@media (max-width: 920px) {
		.board-row {
			grid-template-columns: 1fr;
			gap: 0.2rem;
			padding: 0.4rem;
			background: color-mix(in oklab, var(--chrome-bg) 82%, black);
		}
	}
</style>
