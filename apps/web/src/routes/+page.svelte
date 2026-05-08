<script lang="ts">
	import { onMount } from 'svelte';
	import { navigating, page } from '$app/stores';
	import Header from '$lib/components/board/Header.svelte';
	import ViewTabs from '$lib/components/board/ViewTabs.svelte';
	import SEO from '$lib/components/shell/SEO.svelte';
	import StatPicker from '$lib/components/board/StatPicker.svelte';
	import Board from '$lib/components/board/Board.svelte';
	import Panel from '$lib/components/player/Panel.svelte';
	import { openBoardStream } from '$lib/api/sse';
	import { applyDelta, applySnapshot, boardRows as boardRowsStore, seedBoard } from '$lib/stores/board';

	type SeasonMode = 'live' | 'between' | 'off-game' | 'off-season';

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

	const view = $derived($page.url.searchParams.get('view') ?? 'hitters');
	const isLoading = $derived($navigating !== null);
	const boardRows = $derived($boardRowsStore);
	const selectedPosition = $derived(data.selectedPosition);
	const filteredRows = $derived(
		(() => {
			if (view !== 'positions' || !selectedPosition || selectedPosition === 'all') {
				return boardRows;
			}
			return boardRows.filter((row) => row.position === selectedPosition);
		})()
	);

	let selectedPlayerId = $state<number | null>(null);
	let seasonMode = $state<SeasonMode>('off-season');
	let previewMode = $state(false);
	let streamView = $state('');
	let streamSort = $state('');
	let stop = () => {};

	function handleSelectPlayer(playerId: number) {
		selectedPlayerId = playerId;
	}

	function togglePreviewMode() {
		previewMode = !previewMode;
	}

	function closePanel() {
		selectedPlayerId = null;
	}

	async function refreshSeasonMode() {
		try {
			const response = await fetch('/api/season-state');
			if (!response.ok) return;
			const payload = (await response.json()) as { mode?: SeasonMode };
			seasonMode = payload.mode ?? 'off-season';
		} catch {
			seasonMode = 'off-season';
		}
	}

	onMount(() => {
		void refreshSeasonMode();
		const interval = window.setInterval(() => {
			void refreshSeasonMode();
		}, 30000);
		const handleEscape = (event: KeyboardEvent) => {
			if (event.key === 'Escape') {
				selectedPlayerId = null;
			}
		};
		window.addEventListener('keydown', handleEscape);
		return () => {
			stop();
			window.clearInterval(interval);
			window.removeEventListener('keydown', handleEscape);
		};
	});

	$effect(() => {
		if (streamView === data.boardView && streamSort === data.boardSort) return;
		seedBoard(data.boardView, data.boardSort, data.entries);
		selectedPlayerId = data.entries[0]?.player.id ?? null;
		streamView = data.boardView;
		streamSort = data.boardSort;
	});

	$effect(() => {
		stop();
		const isOffSeason = seasonMode === 'off-season';
		const shouldStream = previewMode || seasonMode !== 'off-season';
		if (isOffSeason && !previewMode) return;
		if (!shouldStream) return;
		const endpoint = previewMode ? '/api/board/preview-sse' : '/api/board/sse';
		const idleMode = !previewMode && (seasonMode === 'between' || seasonMode === 'off-game');
		stop = openBoardStream(
			data.boardView,
			data.boardSort,
			{
				onSnapshot: (payload) => applySnapshot(payload),
				onDelta: (payload) => applyDelta(payload)
			},
			{ endpoint, idleMode }
		);
	});
</script>

<SEO
	title="Diamond Departures · Live Board"
	description="Track live fantasy baseball risers with streaming board updates and player trend details."
	path="/"
/>

<section class="board-screen">
	<Header previewRunning={previewMode} onTogglePreview={togglePreviewMode} />
	{#if previewMode}
		<p class="preview-label" aria-live="polite">preview running · Replay mode</p>
	{/if}
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
			<Board rows={filteredRows} onselect={handleSelectPlayer} />
		{/if}
		<Panel selectedPlayerId={selectedPlayerId} onclose={closePanel} />
	</div>
</section>

<style>
	.board-screen {
		display: grid;
		gap: 0.8rem;
	}

	.preview-label {
		margin: 0;
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.68rem;
		text-transform: uppercase;
		letter-spacing: 0.07em;
		color: color-mix(in oklab, #fcd34d 80%, var(--chrome-text));
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
