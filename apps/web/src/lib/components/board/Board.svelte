<script lang="ts">
	import { onMount } from "svelte";
	import { playRowShift } from "$lib/audio/flap";
	import Row from "./Row.svelte";

	type RowShape = {
		playerId: number;
		rank: string;
		player: string;
		team: string;
		position: string;
		stat: string;
		stats: Record<string, number>;
		justQualified?: boolean;
		qualifiedAt?: string | null;
	};

	let {
		rows = [],
		onselect,
		view = "hitters"
	}: {
		rows?: RowShape[];
		onselect?: (playerId: number) => void;
		view?: string;
	} = $props();

	let previousOrder = $state("");

	const isPitcher = $derived(view.includes("pitcher"));
	const boardStyle = $derived(new URLSearchParams(typeof window !== 'undefined' ? window.location.search : '').get("style") ?? "sabermetric");

	const extraStats = $derived((() => {
		if (isPitcher) {
			return boardStyle === "sabermetric" 
				? ["K/9", "BB/9", "FIP", "xFIP", "WAR"]
				: ["W", "L", "K", "ERA", "WHIP"];
		}
		return boardStyle === "sabermetric"
			? ["wRC+", "OPS+", "WAR", "DRS", "xwOBA"]
			: ["AVG", "HR", "RBI", "SB", "SLG"];
	})());

	$effect(() => {
		const nextOrder = rows.map((row) => row.playerId).join(",");
		if (!previousOrder) {
			previousOrder = nextOrder;
			return;
		}
		if (nextOrder !== previousOrder) {
			playRowShift();
			previousOrder = nextOrder;
		}
	});
</script>

<section class="board" aria-label="leaderboard board">
	<div class="board-rail"></div>
	<div class="board-header-row" role="row">
		<span class="rk-head">RK</span>
		<span class="player-head">PLAYER</span>
		<span>TEAM</span>
		<span>POS</span>
		{#each extraStats as head}
			<span class="stat-head">{head}</span>
		{/each}
		<span class="sort-head">SORT</span>
	</div>
	<div class="board-body" role="rowgroup" aria-live="polite">
		{#each rows as row (row.playerId)}
			<div
				class="row-shell"
				class:just-qualified-enter={Boolean(row.justQualified)}
			>
				<Row {row} onselect={onselect} boardStyle={boardStyle} />
			</div>
		{/each}
	</div>
</section>

<style>
	.board {
		position: relative;
		border-radius: 0.5rem;
		padding: 1rem 0.8rem 0.6rem;
		background: color-mix(in oklab, var(--board-bg) 92%, black);
		border: 1px solid color-mix(in oklab, var(--chrome-text) 18%, transparent);
		overflow: hidden;
	}

	.board-rail {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		height: 3px;
		background: linear-gradient(90deg, var(--mlb-blue) 0%, var(--mlb-blue) 50%, var(--mlb-red) 50%, var(--mlb-red) 100%);
		opacity: 0.8;
	}

	.board-header-row {
		display: grid;
		grid-template-columns: 80px 1fr 100px 80px repeat(5, 100px) 130px;
		gap: 0.4rem;
		padding-bottom: 0.6rem;
		margin-bottom: 0.6rem;
		border-bottom: 1px solid color-mix(in oklab, var(--chrome-text) 14%, transparent);
		font-family: "JetBrains Mono", monospace;
		font-size: 0.65rem;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: color-mix(in oklab, var(--chrome-text) 50%, transparent);
	}

	.rk-head {
		padding-left: 0.4rem;
	}

	.player-head {
		padding-left: 1.2rem;
	}

	.sort-head {
		color: #ffd700;
		text-align: right;
		padding-right: 1.2rem;
	}

	.board-body {
		display: grid;
		gap: 0.25rem;
		max-height: min(82vh, 3000px);
		overflow: auto;
		scrollbar-width: thin;
		scrollbar-color: var(--cell-bg) transparent;
	}

	.row-shell {
		will-change: transform;
		transform: translateZ(0);
		contain: paint;
	}

	.row-shell.just-qualified-enter {
		animation: row-enter 800ms cubic-bezier(0.2, 0.8, 0.2, 1);
	}

	@keyframes row-enter {
		0% {
			opacity: 0;
			transform: translateY(18px);
		}
		100% {
			opacity: 1;
			transform: translateY(0);
		}
	}

	@media (max-width: 920px) {
		.board-header-row {
			display: none;
		}
	}
</style>
