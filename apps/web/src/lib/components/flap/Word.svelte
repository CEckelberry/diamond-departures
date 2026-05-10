<script lang="ts">
	import Cell from './Cell.svelte';
	import { buildCells } from './word.mjs';

	let {
		value,
		width = 12,
		cellWidth = 28,
		cellHeight = 36
	}: {
		value: string;
		width?: number;
		cellWidth?: number;
		cellHeight?: number;
	} = $props();

	const cells = $derived(buildCells(value, width));
</script>

<div class="word" style={`--cells:${width};--cell-width:${cellWidth}px;`} aria-label={`split-flap-word-${value}`}>
	{#each cells as glyph, index (index)}
		<Cell value={glyph} width={cellWidth} height={cellHeight} />
	{/each}
</div>

<style>
	.word {
		display: grid;
		grid-template-columns: repeat(var(--cells), var(--cell-width));
		gap: 2px;
		width: fit-content;
	}
</style>
