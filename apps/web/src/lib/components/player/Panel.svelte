<script lang="ts">
	type TrendChartComponent = typeof import('./TrendChart.svelte').default;
	type PlayerDetail = {
		player: {
			id: number;
			name: string;
			team_abbr: string;
			headshot_url: string;
			position: string;
		};
		season_totals: Record<string, string | number>;
		stat_line: Record<string, string | number>;
		recent_games: Array<Record<string, string | number>>;
	};

	type HistoryPoint = {
		timestamp: string;
		value: number;
	};

	const TREND_STATS = ['wRC+', 'OPS'];

	let { selectedPlayerId }: { selectedPlayerId: number | null } = $props();

	let detail = $state<PlayerDetail | null>(null);
	let loading = $state(false);
	let error = $state('');

	let trendStat = $state('wRC+');
	let historyPoints = $state<HistoryPoint[]>([]);
	let historyLoading = $state(false);
	let historyError = $state('');
	let TrendChart = $state<TrendChartComponent | null>(null);

	$effect(() => {
		if (!selectedPlayerId) {
			detail = null;
			loading = false;
			error = '';
			return;
		}

		const controller = new AbortController();
		loading = true;
		error = '';
		detail = null;

		void fetch(`/api/players/${selectedPlayerId}`, { signal: controller.signal })
			.then(async (response) => {
				if (!response.ok) {
					throw new Error(`player-detail-${response.status}`);
				}
				return (await response.json()) as PlayerDetail;
			})
			.then((payload) => {
				detail = payload;
			})
			.catch((cause: unknown) => {
				if (cause instanceof Error && cause.name === 'AbortError') return;
				error = 'Unable to load player details';
			})
			.finally(() => {
				if (!controller.signal.aborted) loading = false;
			});

		return () => controller.abort();
	});

	$effect(() => {
		if (!selectedPlayerId) {
			historyPoints = [];
			historyLoading = false;
			historyError = '';
			return;
		}

		if (!TrendChart) {
			void (async () => {
				const mod = await import('./TrendChart.svelte');
				TrendChart = mod.default;
			})();
		}

		const controller = new AbortController();
		historyLoading = true;
		historyError = '';
		historyPoints = [];

		void fetch(`/api/players/${selectedPlayerId}/history?stat=${encodeURIComponent(trendStat)}`, {
			signal: controller.signal
		})
			.then(async (response) => {
				if (!response.ok) {
					throw new Error(`player-history-${response.status}`);
				}
				return (await response.json()) as { points: HistoryPoint[] };
			})
			.then((payload) => {
				historyPoints = payload.points ?? [];
			})
			.catch((cause: unknown) => {
				if (cause instanceof Error && cause.name === 'AbortError') return;
				historyError = 'Unable to load trend';
			})
			.finally(() => {
				if (!controller.signal.aborted) historyLoading = false;
			});

		return () => controller.abort();
	});
</script>

<aside class="player-panel" aria-label="Player detail panel">
	{#if !selectedPlayerId}
		<div class="panel-empty">No player selected</div>
	{:else if loading}
		<div class="panel-loading">Loading player details</div>
	{:else if error}
		<div class="panel-error">{error}</div>
	{:else if detail}
		<header class="panel-header">
			<img
				src={detail.player.headshot_url}
				alt={`${detail.player.name} headshot`}
				loading="lazy"
				decoding="async"
				fetchpriority="low"
			/>
			<div>
				<h2>{detail.player.name}</h2>
				<p>{detail.player.team_abbr} · {detail.player.position}</p>
			</div>
		</header>

		<div class="trend-controls">
			{#each TREND_STATS as stat}
				<button class:active={stat === trendStat} onclick={() => (trendStat = stat)}>{stat}</button>
			{/each}
		</div>

		{#if historyLoading}
			<p class="panel-loading">Loading trend…</p>
		{:else if historyError}
			<p class="panel-error">{historyError}</p>
		{:else if TrendChart}
			<TrendChart points={historyPoints} stat={trendStat} />
		{:else}
			<p class="panel-loading">Loading chart…</p>
		{/if}
	{/if}
</aside>

<style>
	.player-panel {
		min-height: 240px;
		padding: 0.8rem;
		border-radius: 0.6rem;
		background: color-mix(in oklab, var(--board-bg) 88%, black);
		border: 1px solid color-mix(in oklab, var(--chrome-text) 16%, transparent);
	}

	.panel-empty,
	.panel-loading,
	.panel-error {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.74rem;
		color: color-mix(in oklab, var(--chrome-text) 82%, transparent);
	}

	.panel-error {
		color: color-mix(in oklab, #ff9f9f 88%, white);
	}

	.panel-header {
		display: flex;
		align-items: center;
		gap: 0.65rem;
		margin-bottom: 0.6rem;
	}

	.panel-header img {
		width: 56px;
		height: 56px;
		border-radius: 50%;
		object-fit: cover;
		background: color-mix(in oklab, var(--chrome-bg) 70%, black);
	}

	.panel-header h2 {
		margin: 0;
		font-size: 1rem;
	}

	.panel-header p {
		margin: 0.2rem 0 0;
		font-size: 0.72rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
	}

	.trend-controls {
		display: flex;
		gap: 0.35rem;
		margin-bottom: 0.55rem;
	}

	.trend-controls button {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.66rem;
		padding: 0.25rem 0.45rem;
		border-radius: 999px;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 25%, transparent);
		background: color-mix(in oklab, var(--chrome-bg) 75%, black);
		color: var(--chrome-text);
	}

	.trend-controls button.active {
		color: var(--cell-text);
		border-color: color-mix(in oklab, var(--cell-text) 45%, transparent);
	}
</style>
