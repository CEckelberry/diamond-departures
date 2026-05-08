<script lang="ts">
	import Header from '$lib/components/board/Header.svelte';
	import ViewTabs from '$lib/components/board/ViewTabs.svelte';
	import StatPicker from '$lib/components/board/StatPicker.svelte';
	import Board from '$lib/components/board/Board.svelte';
	import Panel from '$lib/components/player/Panel.svelte';
	import { boardRows as boardRowsStore, seedBoard } from '$lib/stores/board';

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
			selectedPlayerId: number | null;
		};
	} = $props();

	const boardRows = $derived($boardRowsStore);
	let selectedPlayerId = $state<number | null>(data.selectedPlayerId);

	$effect(() => {
		seedBoard(data.boardView, data.boardSort, data.entries);
		selectedPlayerId = data.selectedPlayerId;
	});

	function handleSelectPlayer(playerId: number) {
		selectedPlayerId = playerId;
	}
</script>

<section class="board-screen">
	<Header />
	<div class="controls">
		<ViewTabs />
		<StatPicker view="hitters" />
	</div>

	<div class="board-layout">
		<Board rows={boardRows} onselect={handleSelectPlayer} />
		<Panel {selectedPlayerId} />
	</div>

	<a class="back-link" href="/">Close panel</a>
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

	.back-link {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.68rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--chrome-text);
		text-decoration: none;
		padding: 0.32rem 0.52rem;
		border-radius: 0.35rem;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 24%, transparent);
		background: color-mix(in oklab, var(--chrome-bg) 80%, black);
		width: fit-content;
	}

	@media (max-width: 1140px) {
		.board-layout {
			grid-template-columns: 1fr;
		}
	}
</style>
