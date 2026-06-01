<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { page } from '$app/stores';
	import Header from '$lib/components/board/Header.svelte';
	import PageTitle from '$lib/components/board/PageTitle.svelte';
	import ViewTabs from '$lib/components/board/ViewTabs.svelte';
	import StatPicker from '$lib/components/board/StatPicker.svelte';
	import Board from '$lib/components/board/Board.svelte';
	import Panel from '$lib/components/player/Panel.svelte';
	import SEO from '$lib/components/shell/SEO.svelte';
	import { openBoardStream } from '$lib/api/sse';
	import { applySnapshot, applyDelta, toBoardRows, anim } from '$lib/stores/board.svelte';
	import type { BoardEntry } from '$lib/stores/board.svelte';

	let { data }: {
		data: {
			boardView: string;
			boardSort: string;
			boardStyle: string;
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

	const rows = $derived(toBoardRows(liveEntries));

	const filteredRows = $derived((() => {
		const { selectedPosition } = data;
		if (view !== 'positions' || !selectedPosition || selectedPosition === 'all') return rows;
		return rows.filter((row) => row.position === selectedPosition);
	})());

	// statCols in Board.svelte reacts to view/style URL params immediately, but
	// liveEntries waits for the server fetch. Without this guard, cells animate
	// through the wrong-data window between URL change and data arrival.
	// Compare against previous values so sort-column clicks (which also trigger
	// $page to update) don't incorrectly set snap.
	let prevPageView = $page.url.searchParams.get('view') ?? 'hitters';
	let prevPageStyle = $page.url.searchParams.get('style') ?? 'sabermetric';
	$effect(() => {
		const v = $page.url.searchParams.get('view') ?? 'hitters';
		const s = $page.url.searchParams.get('style') ?? 'sabermetric';
		if (anim.firstLoadDone && (v !== prevPageView || s !== prevPageStyle)) {
			anim.snap = true;
		}
		prevPageView = v;
		prevPageStyle = s;
	});

	// Seed live entries when load data changes (tab/sort switches).
	// First load: let intro animation play, then mark firstLoadDone so all future
	// cell mounts snap immediately (view switches). anim.snap handles the case
	// where cells stay mounted but all values change at once (sort switches).
	let isFirstDataLoad = true;
	let prevBoardView = data.boardView;
	let prevBoardStyle = data.boardStyle;
	$effect(() => {
		const entries = data.entries;
		const currentView = data.boardView;
		const currentStyle = data.boardStyle;
		if (isFirstDataLoad) {
			isFirstDataLoad = false;
			liveEntries = [...entries];
			tick().then(() => { anim.firstLoadDone = true; });
		} else {
			const isSortOnly = currentView === prevBoardView && currentStyle === prevBoardStyle;
			if (isSortOnly) {
				// Sort column changed: clear any stale snap and let theatrical stagger play
				anim.snap = false;
				liveEntries = [...entries];
			} else {
				// View/style switch: snap all cells to avoid animating wrong-column data
				anim.snap = true;
				liveEntries = [...entries];
				tick().then(() => { anim.snap = false; });
			}
		}
		prevBoardView = currentView;
		prevBoardStyle = currentStyle;
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

	let fps = $state(0);
	const fpsColor = $derived(fps >= 55 ? '#22c55e' : fps >= 30 ? '#f59e0b' : '#ef4444');

	onMount(() => {
		let frames = 0;
		let last = performance.now();
		let raf: number;
		function loop() {
			frames++;
			const now = performance.now();
			if (now - last >= 500) {
				fps = Math.round(frames * 1000 / (now - last));
				frames = 0;
				last = now;
			}
			raf = requestAnimationFrame(loop);
		}
		raf = requestAnimationFrame(loop);
		return () => cancelAnimationFrame(raf);
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

<div class="fps-badge" style="color:{fpsColor}">{fps} <span>fps</span></div>

<SEO title="Diamond Departures · Live Board" description="Live baseball split-flap leaderboard powered by MLB Statcast data." path="/" />

<PageTitle />

<section class="board-screen">
	<div class="top-bar">
		<Header />
		<div class="controls">
			<ViewTabs />
			<StatPicker {view} style={data.boardStyle} />
		</div>
	</div>

	<div class="board-layout">
		<Board rows={filteredRows} view={data.boardView} style={data.boardStyle} sort={data.boardSort} onselect={(id) => { selectedPlayerId = id; }} />
		{#if selectedPlayerId !== null}
			<Panel selectedPlayerId={selectedPlayerId} onclose={closePanel} />
		{/if}
	</div>
</section>

<style>
	.board-screen { display: grid; gap: 0.75rem; padding-top: 0.5rem; }
	.top-bar { display: grid; gap: 0.5rem; background: color-mix(in oklab, var(--chrome-bg) 40%, transparent); padding: 0.5rem 0.75rem; border-radius: 0.6rem; border: 1px solid color-mix(in oklab, var(--chrome-text) 10%, transparent); }
	.controls { display: flex; flex-wrap: wrap; align-items: center; gap: 0.75rem; }
	.board-layout { display: grid; gap: 1rem; grid-template-columns: minmax(0, 1fr); align-items: start; }

	.fps-badge {
		position: fixed;
		bottom: 1rem;
		right: 1rem;
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.7rem;
		font-weight: 700;
		letter-spacing: .04em;
		opacity: 0.6;
		pointer-events: none;
		z-index: 9999;
		transition: color 0.4s;
	}
	.fps-badge span { font-size: 0.55rem; font-weight: 400; opacity: 0.7; }
</style>
