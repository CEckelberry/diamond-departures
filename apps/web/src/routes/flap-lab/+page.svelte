<script lang="ts">
	import Cell from '$lib/components/flap/Cell.svelte';

	const sample = ['8', 'M', 'I', 'D', 'I', 'A', 'M', 'O', 'N', 'D'];
</script>

<main class="lab">
	<h1>Flap lab</h1>
	<div class="row">
		{#each sample as value}
			<Cell {value} />
		{/each}
	</div>
</main>

<style>
	.lab {
		padding: 2rem;
		display: grid;
		gap: 1rem;
	}

	.row {
		display: flex;
		gap: 0.35rem;
		flex-wrap: wrap;
	}
</style>
