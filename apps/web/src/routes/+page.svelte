<script lang="ts">
	import { onMount } from 'svelte';
	import { navigating, page } from '$app/stores';
	import Header from '$lib/components/board/Header.svelte';
	import ViewTabs from '$lib/components/board/ViewTabs.svelte';
	import StatPicker from '$lib/components/board/StatPicker.svelte';
	import Board from '$lib/components/board/Board.svelte';
	import Panel from '$lib/components/player/Panel.svelte';
	import SEO from '$lib/components/shell/SEO.svelte';
	import { openBoardStream } from '$lib/api/sse';
	import { applySnapshot, applyDelta, toBoardRows } from '$lib/stores/board.svelte';
	import type { BoardEntry } from '$lib/stores/board.svelte';

	let { data }: {
		data: {
			boardView: string;
			boardSort: string;
			entries: BoardEntry[];
			selectedPosition: string;
		}
	} = $props();

	let liveEntries = $state<BoardEntry[]>([...data.entries]);
	let seasonMode = $state('off-season');
	let selectedPlayerId = $state<number | null>(null);
	let streamView = $state('');
	let streamSort = $state('');

	const view = $derived($page.url.searchParams.get('view') ?? 'hitters');
	const style = $derived($page.url.searchParams.get('style') ?? 'sabermetric');
	const isLoading = $derived($navigating !== null);

	const rows = $derived(toBoardRows(liveEntries));

	const filteredRows = $derived((() => {
		const { selectedPosition } = data;
		if (view !== 'positions' || !selectedPosition || selectedPosition === 'all') return rows;
		return rows.filter((row) => row.position === selectedPosition);
	})());

	// Seed live entries when load data changes (tab/sort switches)
	$effect(() => {
		liveEntries = [...data.entries];
	});

	onMount(() => {
		fetch('/api/season-state').then((r) => r.json()).then((p) => { seasonMode = p.mode ?? 'off-season'; });
		const interval = setInterval(() => {
			fetch('/api/season-state').then((r) => r.json()).then((p) => { seasonMode = p.mode ?? 'off-season'; });
		}, 30000);
		return () => clearInterval(interval);
	});

	// SSE stream — only open when not off-season, guard against churn on same view/sort
	$effect(() => {
		if (seasonMode === 'off-season') return;
		if (streamView === data.boardView && streamSort === data.boardSort) return;
		streamView = data.boardView;
		streamSort = data.boardSort;

		const idleMode = seasonMode !== 'off-season' && seasonMode !== 'live';

		const stop = openBoardStream(
			data.boardView,
			data.boardSort,
			{
				onSnapshot: (p) => { liveEntries = applySnapshot(p); },
				onDelta: (p) => { liveEntries = applyDelta(liveEntries, p); }
			},
			{ endpoint: '/api/board/sse', idleMode }
		);

		return () => { stop(); };
	});

	function closePanel() {
		selectedPlayerId = null;
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') {
			selectedPlayerId = null;
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />

<SEO title="Diamond Departures · Live Board" description="Live baseball split-flap leaderboard powered by MLB Statcast data." path="/" />

<section class="board-screen">
	<div class="top-bar">
		<Header />
		<div class="controls">
			<ViewTabs />
			<StatPicker {view} />
		</div>
	</div>

	<div class="board-layout">
		{#if isLoading}
			<div class="board-skeleton">Loading...</div>
		{:else}
			<Board rows={filteredRows} {view} {style} sort={data.boardSort} onselect={(id) => { selectedPlayerId = id; }} />
			{#if selectedPlayerId !== null}
				<Panel selectedPlayerId={selectedPlayerId} onclose={closePanel} />
			{/if}
		{/if}
	</div>
</section>

<style>
	.board-screen { display: grid; gap: 0.75rem; padding-top: 0.5rem; }
	.top-bar { display: grid; gap: 0.5rem; background: color-mix(in oklab, var(--chrome-bg) 40%, transparent); padding: 0.5rem 0.75rem; border-radius: 0.6rem; border: 1px solid color-mix(in oklab, var(--chrome-text) 10%, transparent); }
	.controls { display: flex; flex-wrap: wrap; align-items: center; gap: 0.75rem; }
	.board-layout { display: grid; gap: 1rem; grid-template-columns: minmax(0, 1fr); align-items: start; }
</style>
