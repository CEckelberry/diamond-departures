<script lang="ts">
	import { onMount } from 'svelte';
	import { flip } from 'svelte/animate';
	import { cubicOut } from 'svelte/easing';
	import { goto, preloadData } from '$app/navigation';
	import { page } from '$app/stores';
	import { playRowShift } from '$lib/audio/flap';
	import Row from './Row.svelte';
	import type { BoardRow } from './types';
	import { anim } from '$lib/stores/board.svelte';

	const HITTER_TRAD_COLS  = ['AVG', 'HR', 'RBI', 'OBP', 'SLG', 'SB', 'OPS'];
	const HITTER_SABER_COLS = ['wOBA', 'wRC+', 'BABIP', 'ISO', 'BB%', 'K%', 'OPS'];
	const PITCHER_TRAD_COLS  = ['ERA', 'W', 'L', 'WHIP', 'K', 'SV', 'BB/9'];
	const PITCHER_SABER_COLS = ['FIP', 'K-BB%', 'K%', 'BB%', 'ERA', 'WHIP', 'K/9'];

	let {
		rows = [],
		view = 'hitters',
		style = 'sabermetric',
		sort = '',
		onselect
	}: {
		rows?: BoardRow[];
		view?: string;
		style?: string;
		sort?: string;
		onselect?: (playerId: number) => void;
	} = $props();

	const statCols = $derived(
		view.startsWith('pitcher')
			? (style === 'traditional' ? PITCHER_TRAD_COLS : PITCHER_SABER_COLS)
			: (style === 'traditional' ? HITTER_TRAD_COLS : HITTER_SABER_COLS)
	);

	const PLACEHOLDER: BoardRow = {
		playerId: 0,
		rank: '   ',
		player: '                  ',
		team: '   ',
		position: '  ',
		stat: '     ',
		stats: {},
		justQualified: false,
		qualifiedAt: null
	};

	// ?rows=N in the URL caps displayed rows for performance debugging
	const debugMaxRows = $derived(
		typeof window !== 'undefined'
			? (parseInt(new URLSearchParams(window.location.search).get('rows') ?? '') || 100)
			: 100
	);

	const placeholderRows = $derived(
		Array.from({ length: debugMaxRows }, (_, i) => rows[i] ?? { ...PLACEHOLDER, playerId: -(i + 1) })
	);

	let reducedMotion = $state(false);
	let boardBodyEl: HTMLElement;

	// Approx animated cells per row: rank(3) + name(18) + team(3) + pos(2) + 7 stat cols × 5 chars
	// Use a round number that matches the perf-demo sweet spot rather than the theoretical max.
	const CELLS_PER_ROW = 50;

	onMount(() => {
		const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
		reducedMotion = mq.matches;
		const handler = (e: MediaQueryListEvent) => { reducedMotion = e.matches; };
		mq.addEventListener('change', handler);

		// Recompute animation density whenever the board's visible height changes so we
		// never push more than ~364 simultaneous CSS 3D layers to the GPU.
		const computeDensity = () => {
			const firstRow = boardBodyEl?.querySelector('.row-shell') as HTMLElement | null;
			const rowH = (firstRow?.getBoundingClientRect().height) || 40;
			anim.adjustForViewport(boardBodyEl.clientHeight, rowH, CELLS_PER_ROW);
		};
		const ro = new ResizeObserver(computeDensity);
		ro.observe(boardBodyEl);
		computeDensity(); // set before first render cycle completes

		return () => {
			mq.removeEventListener('change', handler);
			ro.disconnect();
		};
	});

	let previousOrder = '';
	$effect(() => {
		const order = rows.map((r) => r.playerId).join(',');
		if (previousOrder && order !== previousOrder) playRowShift();
		previousOrder = order;
	});

	const SORTABLE_STATS = new Set([
		'wRC+', 'wOBA', 'OPS', 'AVG', 'HR', 'RBI', 'SLG', 'SB', 'BABIP', 'ISO', 'BB%', 'K%',
		'ERA', 'FIP', 'WHIP', 'W', 'L', 'SV', 'K', 'K/9', 'BB/9', 'K-BB%'
	]);

	function sortUrl(stat: string): string {
		const url = new URL($page.url);
		url.searchParams.set('sort', stat);
		return url.toString();
	}

	function handleColClick(stat: string) {
		if (!SORTABLE_STATS.has(stat)) return;
		goto(sortUrl(stat));
	}

	function handleColHover(stat: string) {
		if (!SORTABLE_STATS.has(stat) || stat === sort) return;
		preloadData(sortUrl(stat));
	}
</script>

<section
	class="board"
	aria-label="leaderboard board"
	aria-live="polite"
>
	<div class="board-rail"></div>
	<div class="board-header-row">
		<span class="rk-head">RK</span>
		<span>PLAYER</span>
		<span>TEAM</span>
		<span>POS</span>
		{#each statCols as col}
			<span
				class="stat-col-head"
				class:stat-head={col === sort}
				class:sortable={SORTABLE_STATS.has(col)}
				onclick={() => handleColClick(col)}
				onmouseenter={() => handleColHover(col)}
				role={SORTABLE_STATS.has(col) ? 'button' : undefined}
				tabindex={SORTABLE_STATS.has(col) ? 0 : undefined}
				onkeydown={(e: KeyboardEvent) => { if (e.key === 'Enter') handleColClick(col); }}
			>{col}</span>
		{/each}
	</div>
	<div class="board-body" bind:this={boardBodyEl}>
		{#each placeholderRows as row, index (row.playerId)}
			<div
				class="row-shell"
				animate:flip={{ delay: index * 30, duration: reducedMotion ? 0 : 300, easing: cubicOut }}
			>
				<div class:row-enter={row.justQualified}>
					<Row {row} rowIndex={index} {sort} {statCols} onselect={onselect} />
				</div>
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
		grid-template-columns: 3.5rem 21rem 5rem 4rem repeat(7, minmax(5rem, 1fr));
		gap: 0.6rem;
		border-bottom: 1px solid color-mix(in oklab, var(--chrome-text) 14%, transparent);
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.65rem;
		text-transform: uppercase;
		color: color-mix(in oklab, var(--chrome-text) 50%, transparent);
		padding-bottom: 0.5rem;
		margin-bottom: 0.5rem;
	}

	.rk-head { padding-left: 0.4rem; }

	.stat-col-head {
		text-align: center;
	}

	.stat-col-head.sortable {
		cursor: pointer;
	}

	.stat-col-head.sortable:hover {
		color: color-mix(in oklab, var(--chrome-text) 90%, white);
	}

	.stat-head {
		color: #fbbf24;
		font-weight: 700;
		background: rgba(251, 191, 36, 0.1);
		border-radius: 0.2rem;
		padding: 0.1rem 0.3rem;
	}

	.board-body {
		display: grid;
		gap: 0.25rem;
		max-height: 80vh;
		overflow: auto;
	}

	.row-shell {
		transform: translateZ(0);
		contain: layout paint;
	}

	.row-enter {
		animation: row-enter 800ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
	}

	@keyframes row-enter {
		from { transform: translateY(40px) translateZ(0); opacity: 0; }
		to { transform: translateY(0) translateZ(0); opacity: 1; }
	}

	@media (prefers-reduced-motion: reduce) {
		.row-enter { animation: none; }
	}

	@media (max-width: 920px) {
		.board-header-row {
			display: none;
		}

		.board {
			padding: 0.5rem 0.25rem;
		}
	}
</style>
