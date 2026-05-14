<script lang="ts">
	import { onMount, untrack } from "svelte";
	import { navigating, page } from "$app/stores";
	import Header from "$lib/components/board/Header.svelte";
	import ViewTabs from "$lib/components/board/ViewTabs.svelte";
	import Board from "$lib/components/board/Board.svelte";
	import { openBoardStream } from "$lib/api/sse";
	import { toBoardRows } from "$lib/stores/board.svelte";

	let { data } = $props();

	let liveEntries = $state<any[]>([]);
	
	// React to prop changes (tab navigation)
	$effect(() => {
		const { entries } = data;
		untrack(() => {
			liveEntries = [...entries];
		});
	});

	const rows = $derived(toBoardRows(liveEntries.length > 0 ? liveEntries : data.entries));
	const view = $derived($page.url.searchParams.get("view") ?? "hitters");
	const isLoading = $derived($navigating !== null);

	let seasonMode = $state("off-season");
	onMount(() => {
		fetch("/api/season-state").then(r => r.json()).then(p => seasonMode = p.mode ?? "off-season");
		const interval = setInterval(() => {
			fetch("/api/season-state").then(r => r.json()).then(p => seasonMode = p.mode ?? "off-season");
		}, 30000);
		return () => clearInterval(interval);
	});

	$effect(() => {
		if (seasonMode === "off-season") return;
		const cleanup = openBoardStream(data.boardView, data.boardSort, {
			onSnapshot: (p) => { liveEntries = [...p.entries]; },
			onDelta: (p) => {
				const next = [...liveEntries];
				for (const change of p.changes) {
					const entry = next.find(item => item.player.id === change.player_id);
					if (entry) {
						if (change.new_rank) entry.rank = change.new_rank;
						for (const s of change.changed_stats) {
							if (s.name === "stat_value") entry.stat_value = Number(s.new);
						}
					}
				}
				next.sort((a, b) => a.rank - b.rank);
				liveEntries = next;
			}
		}, { endpoint: "/api/board/sse", idleMode: seasonMode !== "live" });
		return cleanup;
	});
</script>

<section class="board-screen">
	<div class="top-bar">
		<Header />
		<div class="controls"><ViewTabs /></div>
	</div>
	<div class="board-layout">
		{#if isLoading}
			<div class="board-skeleton">Loading...</div>
		{:else}
			<Board {rows} {view} />
		{/if}
	</div>
</section>

<style>
	.board-screen { display: grid; gap: 0.75rem; padding-top: 0.5rem; }
	.top-bar { display: grid; gap: 0.5rem; background: color-mix(in oklab, var(--chrome-bg) 40%, transparent); padding: 0.5rem 0.75rem; border-radius: 0.6rem; border: 1px solid color-mix(in oklab, var(--chrome-text) 10%, transparent); }
	.board-layout { display: grid; grid-template-columns: 1fr; align-items: start; }
</style>
