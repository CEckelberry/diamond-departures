<script lang="ts">
	import Cell from "./Cell.svelte";
	import { buildCells } from "./word.mjs";

	let {
		value,
		width = 12,
		cellWidth = 28,
		cellHeight = 36,
		rowIndex = 0,
		baseColIndex = 0
	} = $props();

	const cells = $derived(buildCells(value, width));
</script>

<div class="word" style="--cells:{width};--cell-width:{cellWidth}px;">
	{#each cells as char, index}
		{#if char === " "}
			<div class="empty-cell" style="width:{cellWidth}px; height:{cellHeight}px;"></div>
		{:else}
			<Cell 
				value={char} 
				width={cellWidth} 
				height={cellHeight} 
				staggerIndex={rowIndex * 4 + baseColIndex + index}
				rowIndex={rowIndex}
			/>
		{/if}
	{/each}
</div>

<style>
	.word {
		display: grid;
		grid-template-columns: repeat(var(--cells), var(--cell-width));
		gap: 2px;
		width: fit-content;
	}

	.empty-cell {
		position: relative;
		border-radius: 4px;
		background: var(--cell-bg);
		box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--cell-edge) 60%, transparent), 0 2px 4px rgba(0,0,0,0.5);
	}

	.empty-cell::after {
		content: "";
		position: absolute;
		top: calc(50% - 0.5px);
		left: 0;
		width: 100%;
		height: 1px;
		background: color-mix(in oklab, var(--cell-edge) 80%, black);
	}
</style>
