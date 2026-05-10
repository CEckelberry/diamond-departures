<script lang="ts">
	import { onMount, untrack } from "svelte";
	import { navigating, page } from "$app/stores";
	import Header from "$lib/components/board/Header.svelte";
	import ViewTabs from "$lib/components/board/ViewTabs.svelte";
	import SEO from "$lib/components/shell/SEO.svelte";

	import Board from "$lib/components/board/Board.svelte";
	import { openBoardStream } from "$lib/api/sse";
	import { applyDelta, applySnapshot, boardRows as boardRowsStore, seedBoard } from "$lib/stores/board";

	type SeasonMode = "live" | "between" | "off-game" | "off-season";

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
		additional_stats: Record<string, number>;
		freshness: {
			timestamp: string;
			age_category: "live" | "recent" | "stale" | "old";
		};
	};

	let {
		data
	}: {
		data: {
			boardView: string;
			boardSort: string;
			entries: BoardEntryPayload[];
			selectedPosition: string;
		};
	} = $props();

	const view = $derived($page.url.searchParams.get("view") ?? "hitters");
	const isLoading = $derived($navigating !== null);
	const boardRows = $derived($boardRowsStore);
	const selectedPosition = $derived(data.selectedPosition);
	const filteredRows = $derived(
		(() => {
			const rows = boardRows;
			if (view !== "positions" || !selectedPosition || selectedPosition === "all") {
				return rows;
			}
			return rows.filter((row) => row.position === selectedPosition);
		})()
	);

	let selectedPlayerId = $state<number | null>(null);
	let seasonMode = $state<SeasonMode>("off-season");

	function handleSelectPlayer(playerId: number) {
		selectedPlayerId = playerId;
	}

	async function refreshSeasonMode() {
		try {
			const response = await fetch("/api/season-state");
			if (!response.ok) return;
			const payload = (await response.json()) as { mode?: SeasonMode };
			seasonMode = payload.mode ?? "off-season";
		} catch {
			seasonMode = "off-season";
		}
	}

	onMount(() => {
		void refreshSeasonMode();
		const interval = window.setInterval(() => {
			void refreshSeasonMode();
		}, 30000);
		const handleEscape = (event: KeyboardEvent) => {
			if (event.key === "Escape") {
				selectedPlayerId = null;
			}
		};
		window.addEventListener("keydown", handleEscape);
		return () => {
			window.clearInterval(interval);
			window.removeEventListener("keydown", handleEscape);
		};
	});

	let lastSeeded = "";

	$effect(() => {
		const key = data.boardView + "-" + data.boardSort;
		if (key === lastSeeded) return;
		lastSeeded = key;
		
		untrack(() => seedBoard(data.boardView, data.boardSort, data.entries));
	});

	$effect(() => {
		if (seasonMode === "off-season") return;
		
		const v = data.boardView;
		const s = data.boardSort;
		
		let streamCleanup: (() => void) | null = null;
		
		const timeout = window.setTimeout(() => {
			const endpoint = "/api/board/sse";
			const idleMode = (seasonMode === "between" || seasonMode === "off-game");
			
			streamCleanup = openBoardStream(
				v,
				s,
				{
					onSnapshot: (payload) => applySnapshot(payload),
					onDelta: (payload) => applyDelta(payload)
				},
				{ endpoint, idleMode }
			);
		}, 400);

		return () => {
			window.clearTimeout(timeout);
			if (streamCleanup) streamCleanup();
		};
	});
</script>

<SEO
	title="Diamond Departures · Live Board"
	description="Track live fantasy baseball risers with streaming board updates and player trend details."
	path="/"
/>

<section class="board-screen">
	<div class="top-bar">
		<Header />
		<div class="controls">
			<ViewTabs />
		</div>
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
			<Board rows={filteredRows} onselect={handleSelectPlayer} view={view} />
		{/if}
	</div>
</section>

<style>
	.board-screen {
		display: grid;
		gap: 0.75rem;
		padding-top: 0.5rem;
	}

	.top-bar {
		display: grid;
		gap: 0.5rem;
		background: color-mix(in oklab, var(--chrome-bg) 40%, transparent);
		padding: 0.5rem 0.75rem;
		border-radius: 0.6rem;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 10%, transparent);
	}

	.controls {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		justify-content: space-between;
		gap: 0.5rem;
	}

	.board-layout {
		display: grid;
		gap: 1rem;
		grid-template-columns: 1fr;
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
