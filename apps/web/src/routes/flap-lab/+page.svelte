<script lang="ts">
	import Cell from '$lib/components/flap/Cell.svelte';
	import Word from '$lib/components/flap/Word.svelte';

	const sample = ['8', 'M', 'I', 'D', 'I', 'A', 'M', 'O', 'N', 'D'];
	let score = $state('98');
</script>

<main class="lab">
	<h1>Flap lab</h1>
	<div class="row">
		{#each sample as value}
			<Cell {value} />
		{/each}
	</div>

	<button type="button" class="demo" onclick={() => (score = score === '98' ? '172' : '98')}>
		Toggle score ({score})
	</button>

	<Word value={score} width={5} />
	<Word value="JUDGE, A." width={12} />
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

	.demo {
		width: fit-content;
		padding: 0.4rem 0.7rem;
		border-radius: 0.35rem;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 30%, transparent);
		background: transparent;
		color: inherit;
		font-family: 'JetBrains Mono', monospace;
	}
</style>
