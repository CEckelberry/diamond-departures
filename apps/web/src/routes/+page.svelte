<script lang="ts">
	import { onMount } from 'svelte';
	import { navigating, page } from '$app/stores';
	import Header from '$lib/components/board/Header.svelte';
	import ViewTabs from '$lib/components/board/ViewTabs.svelte';
	import StatPicker from '$lib/components/board/StatPicker.svelte';
	import Board from '$lib/components/board/Board.svelte';
	import Panel from '$lib/components/player/Panel.svelte';
	import { openBoardStream } from '$lib/api/sse';
	import { applyDelta, applySnapshot, boardRows as boardRowsStore, seedBoard } from '$lib/stores/board';

	type BoardEntryPayload = {
		rank: number;
		player: {
			id: number;
			name: string;
			team_abbr: string;
			headshot_url: string;
			position: string;
		};
		stat_value: number;
		freshness: {
			timestamp: string;
			age_category: 'live' | 'recent' | 'stale' | 'old';
		};
	};

	let { data }: { data: { boardView: string; boardSort: string; entries: BoardEntryPayload[] } } = $props();

	const view = $derived($page.url.searchParams.get('view') ?? 'hitters');
	const isLoading = $derived($navigating !== null);
	const boardRows = $derived($boardRowsStore);

	let selectedPlayerId = $state<number | null>(null);
	let stop = () => {};

	function handleSelectPlayer(playerId: number) {
		selectedPlayerId = playerId;
	}

	onMount(() => {
		return () => {
			stop();
		};
	});

	$effect(() => {
		seedBoard(data.boardView, data.boardSort, data.entries);
		selectedPlayerId = data.entries[0]?.player.id ?? null;
		stop();
		stop = openBoardStream(data.boardView, data.boardSort, {
			onSnapshot: (payload) => applySnapshot(payload),
			onDelta: (payload) => applyDelta(payload)
		});
	});
</script>

<section class="board-screen">
	<Header />
	<div class="controls">
		<ViewTabs />
		<StatPicker {view} />
	</div>

	<div class="board-layout">
		{#if isLoading}
			<div class="board-skeleton" aria-label="Loading board">
				<div class="skeleton-row"></div>
				<div class="skeleton-row"></div>
				<div class="skeleton-row"></div>
				<div class="skeleton-row"></div>
			</div>
		{:else}
			<Board rows={boardRows} onselect={handleSelectPlayer} />
		{/if}
		<Panel selectedPlayerId={selectedPlayerId} />
	</div>
</section>

<style>
	.board-screen {
		display: grid;
		gap: 0.8rem;
	}

	.controls {
		display: grid;
		gap: 0.5rem;
	}

	.board-layout {
		display: grid;
		gap: 0.7rem;
		grid-template-columns: minmax(0, 1fr) minmax(240px, 300px);
		align-items: start;
	}

	.board-skeleton {
		display: grid;
		gap: 0.35rem;
		padding: 0.8rem;
		border-radius: 0.6rem;
		background: color-mix(in oklab, var(--board-bg) 90%, black);
		border: 1px solid color-mix(in oklab, var(--chrome-text) 14%, transparent);
	}

	.skeleton-row {
		height: 36px;
		border-radius: 0.35rem;
		background: linear-gradient(
			90deg,
			color-mix(in oklab, var(--chrome-bg) 60%, transparent) 25%,
			color-mix(in oklab, var(--chrome-bg) 30%, white) 50%,
			color-mix(in oklab, var(--chrome-bg) 60%, transparent) 75%
		);
		background-size: 220% 100%;
		animation: board-skeleton-slide 1.1s ease-in-out infinite;
	}

	@keyframes board-skeleton-slide {
		0% {
			background-position: 120% 0;
		}
		100% {
			background-position: -120% 0;
		}
	}

	@media (max-width: 1140px) {
		.board-layout {
			grid-template-columns: 1fr;
		}
	}
</style>
