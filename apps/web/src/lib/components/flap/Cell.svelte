<script lang="ts">
	let { value, width = 28, height = 36 }: { value: string; width?: number; height?: number } = $props();

	const glyph = $derived((value ?? ' ').slice(0, 1).toUpperCase());
	const half = $derived(Math.floor(height / 2));
</script>

<div
	class="cell"
	style={`--cell-width:${width}px;--cell-height:${height}px;--half-height:${half}px;`}
	aria-label={`split-flap-cell-${glyph}`}
>
	<div class="face top" aria-hidden="true">
		<span>{glyph}</span>
	</div>
	<div class="hairline" aria-hidden="true"></div>
	<div class="face bottom" aria-hidden="true">
		<span>{glyph}</span>
	</div>
</div>

<style>
	.cell {
		position: relative;
		display: inline-block;
		width: var(--cell-width);
		height: var(--cell-height);
		border-radius: 3px;
		overflow: hidden;
		background: var(--cell-bg);
		box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--cell-edge) 60%, transparent);
		font-family: 'JetBrains Mono', monospace;
		font-weight: 700;
		color: var(--cell-text);
	}

	.face {
		position: absolute;
		left: 0;
		width: 100%;
		height: var(--half-height);
		overflow: hidden;
		display: flex;
		justify-content: center;
		text-shadow: 0 1px 0 color-mix(in oklab, var(--cell-text-dim) 70%, transparent);
	}

	.face span {
		position: absolute;
		left: 50%;
		top: 50%;
		transform: translate(-50%, -50%);
		line-height: 1;
		font-size: calc(var(--cell-height) * 0.62);
	}

	.top {
		top: 0;
		background: linear-gradient(
			to bottom,
			color-mix(in oklab, var(--cell-bg) 85%, white),
			var(--cell-bg)
		);
	}

	.bottom {
		bottom: 0;
		background: linear-gradient(
			to top,
			color-mix(in oklab, var(--cell-bg) 88%, black),
			var(--cell-bg)
		);
	}

	.bottom span {
		transform: translate(-50%, calc(-50% - var(--half-height)));
	}

	.hairline {
		position: absolute;
		top: calc(50% - 0.5px);
		left: 0;
		width: 100%;
		height: 1px;
		background: color-mix(in oklab, var(--cell-edge) 75%, black);
		z-index: 2;
	}
</style>
