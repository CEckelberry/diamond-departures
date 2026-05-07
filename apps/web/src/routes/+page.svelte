<script lang="ts">
	import { page } from '$app/stores';
	import Header from '$lib/components/board/Header.svelte';
	import ViewTabs from '$lib/components/board/ViewTabs.svelte';
	import StatPicker from '$lib/components/board/StatPicker.svelte';
	import Board from '$lib/components/board/Board.svelte';

	const view = $derived($page.url.searchParams.get('view') ?? 'hitters');
</script>

<section class="board-screen">
	<Header />
	<div class="controls">
		<ViewTabs />
		<StatPicker {view} />
	</div>
	<Board />
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
</style>
