<script lang="ts">
	import { flip } from 'svelte/animate';
	import { cubicOut } from 'svelte/easing';
	import { playRowShift } from '$lib/audio/flap';
	import Row from './Row.svelte';
	import type { BoardRow } from './types';

	let {
		rows = [],
		view = 'hitters',
		onselect
	}: {
		rows?: BoardRow[];
		view?: string;
		onselect?: (playerId: number) => void;
	} = $props();

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

	const placeholderRows = $derived(
		Array.from({ length: 100 }, (_, i) => rows[i] ?? { ...PLACEHOLDER, playerId: -(i + 1) })
	);

	let reducedMotion = $state(false);
	if (typeof window !== 'undefined') {
		const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
		reducedMotion = mq.matches;
		mq.addEventListener('change', (e) => { reducedMotion = e.matches; });
	}

	let previousOrder = '';
	$effect(() => {
		const order = rows.map((r) => r.playerId).join(',');
		if (previousOrder && order !== previousOrder) playRowShift();
		previousOrder = order;
	});
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
		<span>STAT</span>
	</div>
	<div class="board-body">
		{#each placeholderRows as row, index (row.playerId)}
			<div
				class="row-shell"
				class:row-enter={row.justQualified}
				animate:flip={{ delay: index * 30, duration: reducedMotion ? 0 : 300, easing: cubicOut }}
				style="transform: translateZ(0); contain: layout paint;"
			>
				<Row {row} rowIndex={index} onselect={onselect} />
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
		grid-template-columns: 3.5rem 20rem 6rem 6rem 8rem;
		gap: 0.4rem;
		border-bottom: 1px solid color-mix(in oklab, var(--chrome-text) 14%, transparent);
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.65rem;
		text-transform: uppercase;
		color: color-mix(in oklab, var(--chrome-text) 50%, transparent);
		padding-bottom: 0.5rem;
		margin-bottom: 0.5rem;
	}

	.rk-head { padding-left: 0.4rem; }

	.board-body {
		display: grid;
		gap: 0.25rem;
		max-height: 80vh;
		overflow: auto;
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
