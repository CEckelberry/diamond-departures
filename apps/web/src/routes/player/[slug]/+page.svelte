<script lang="ts">
	import { onMount } from 'svelte';
	import Header from '$lib/components/board/Header.svelte';
	import ViewTabs from '$lib/components/board/ViewTabs.svelte';
	import Board from '$lib/components/board/Board.svelte';
	import Panel from '$lib/components/player/Panel.svelte';
	import SEO from '$lib/components/shell/SEO.svelte';
	import { applySnapshot, applyDelta, toBoardRows } from '$lib/stores/board.svelte';
	import { openBoardStream } from '$lib/api/sse';
	import type { BoardEntry } from '$lib/stores/board.svelte';

	let { data }: {
		data: {
			boardView: string;
			boardSort: string;
			entries: BoardEntry[];
			selectedPlayerId: number | null;
			selectedSlug: string;
		}
	} = $props();

	let liveEntries = $state<BoardEntry[]>([...data.entries]);
	let selectedPlayerId = $state<number | null>(data.selectedPlayerId);

	const boardRows = $derived(toBoardRows(liveEntries));

	$effect(() => {
		liveEntries = [...data.entries];
		selectedPlayerId = data.selectedPlayerId;
	});

	onMount(() => {
		const stop = openBoardStream(data.boardView, data.boardSort, {
			onSnapshot: (p) => { liveEntries = applySnapshot(p); },
			onDelta: (p) => { liveEntries = applyDelta(liveEntries, p); }
		}, { endpoint: '/api/board/sse' });
		return () => { stop(); };
	});

	function handleSelectPlayer(playerId: number) {
		selectedPlayerId = playerId;
	}

	function closePanel() {
		selectedPlayerId = null;
	}
</script>

<SEO
	title="Diamond Departures · Player Detail"
	description="Single-player departure board view with trend panel and live row updates."
	path="/player"
/>

<section class="board-screen">
	<Header />
	<div class="controls">
		<ViewTabs />
	</div>

	<div class="board-layout">
		<Board rows={boardRows} onselect={handleSelectPlayer} />
		<Panel {selectedPlayerId} onclose={closePanel} />
	</div>

	<a class="back-link" href="/">Back to board</a>
</section>

<style>
	.board-screen { display: grid; gap: 0.8rem; }
	.controls { display: grid; gap: 0.5rem; }
	.board-layout { display: grid; gap: 0.7rem; grid-template-columns: minmax(0, 1fr) minmax(240px, 300px); align-items: start; }
	.back-link { display: inline-flex; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--chrome-text); text-decoration: none; padding: 0.32rem 0.52rem; border-radius: 0.35rem; border: 1px solid color-mix(in oklab, var(--chrome-text) 24%, transparent); background: color-mix(in oklab, var(--chrome-bg) 80%, black); width: fit-content; }
</style>
