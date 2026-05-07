<script lang="ts">
	type HistoryPoint = {
		timestamp: string;
		value: number;
	};

	let {
		points,
		stat
	}: {
		points: HistoryPoint[];
		stat: string;
	} = $props();

	const WIDTH = 260;
	const HEIGHT = 96;
	const PADDING = 8;

	function polylinePoints() {
		if (points.length === 0) return '';
		const values = points.map((point) => point.value);
		const min = Math.min(...values);
		const max = Math.max(...values);
		const span = max - min || 1;
		const xStep = points.length === 1 ? 0 : (WIDTH - PADDING * 2) / (points.length - 1);
		return points
			.map((point, index) => {
				const x = PADDING + index * xStep;
				const normalized = (point.value - min) / span;
				const y = HEIGHT - PADDING - normalized * (HEIGHT - PADDING * 2);
				return `${x.toFixed(2)},${y.toFixed(2)}`;
			})
			.join(' ');
	}
</script>

<figure class="trend-chart">
	<svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} aria-label="Player trend chart" role="img">
		<polyline points={polylinePoints()} class="trend-line" />
	</svg>
	<figcaption class="chart-caption">trend-stat: {stat}</figcaption>
</figure>

<style>
	.trend-chart {
		margin: 0;
		display: grid;
		gap: 0.3rem;
	}

	svg {
		width: 100%;
		height: auto;
		border-radius: 0.45rem;
		background: color-mix(in oklab, var(--chrome-bg) 62%, black);
		border: 1px solid color-mix(in oklab, var(--chrome-text) 18%, transparent);
	}

	.trend-line {
		fill: none;
		stroke: color-mix(in oklab, var(--cell-text) 88%, white);
		stroke-width: 2.25;
		stroke-linecap: round;
		stroke-linejoin: round;
	}

	.chart-caption {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.62rem;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: color-mix(in oklab, var(--chrome-text) 72%, transparent);
	}
</style>
