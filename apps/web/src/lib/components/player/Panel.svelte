<script lang="ts">
	import { userStore } from '$lib/stores/user';

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

	let {
		selectedPlayerId,
		onclose
	}: {
		selectedPlayerId: number | null;
		onclose?: () => void;
	} = $props();

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

	// Email alerts
	let alerts = $state<any[]>([]);
	let alertStat = $state('wRC+');
	let alertThreshold = $state('');
	let alertDirection = $state<'up' | 'down'>('up');

	async function loadAlerts(playerId: number) {
		if (!$userStore?.is_premium) return;
		const resp = await fetch('/api/alerts');
		if (resp.ok) {
			const all = await resp.json();
			alerts = all.filter((a: any) => a.player_id === playerId);
		}
	}

	async function createAlert() {
		const threshold = parseFloat(alertThreshold);
		if (isNaN(threshold) || !selectedPlayerId) return;
		const resp = await fetch('/api/alerts', {
			method: 'POST',
			headers: { 'content-type': 'application/json' },
			body: JSON.stringify({
				player_id: selectedPlayerId,
				stat_name: alertStat,
				threshold,
				direction: alertDirection,
			}),
		});
		if (resp.ok) {
			alerts = [...alerts, await resp.json()];
			alertThreshold = '';
		}
	}

	async function deleteAlert(id: string) {
		await fetch(`/api/alerts/${id}`, { method: 'DELETE' });
		alerts = alerts.filter((a) => a.id !== id);
	}

	$effect(() => {
		if (selectedPlayerId) {
			loadAlerts(selectedPlayerId);
		} else {
			alerts = [];
		}
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
			<button class="close-button" type="button" onclick={() => onclose?.()} aria-label="Close player detail panel">
				Close
			</button>
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

		{#if $userStore?.is_premium && selectedPlayerId}
			<div class="alerts-section">
				<h3 class="alerts-title">Email Alerts</h3>
				{#each alerts as alert (alert.id)}
					<div class="alert-row">
						<span class="alert-label">{alert.stat_name} {alert.direction === 'up' ? '≥' : '≤'} {alert.threshold}</span>
						<button class="alert-del" onclick={() => deleteAlert(alert.id)}>✕</button>
					</div>
				{/each}
				<div class="alert-form">
					<select class="alert-select" bind:value={alertStat}>
						<option>wRC+</option>
						<option>OPS</option>
						<option>ERA</option>
						<option>FIP</option>
						<option>K%</option>
						<option>AVG</option>
						<option>HR</option>
					</select>
					<select class="alert-select" bind:value={alertDirection}>
						<option value="up">≥</option>
						<option value="down">≤</option>
					</select>
					<input
						class="alert-input"
						bind:value={alertThreshold}
						placeholder="threshold"
						type="number"
						step="0.1"
					/>
					<button class="alert-add" onclick={createAlert}>Add</button>
				</div>
			</div>
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
		display: grid;
		grid-template-columns: auto 1fr;
		align-items: center;
		gap: 0.65rem;
		margin-bottom: 0.6rem;
	}

	.close-button {
		grid-column: 1 / -1;
		justify-self: end;
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.68rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		padding: 0.2rem 0.4rem;
		border-radius: 0.3rem;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 25%, transparent);
		background: transparent;
		color: var(--chrome-text);
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

	.alerts-section {
		padding: 1rem;
		border-top: 1px solid color-mix(in oklab, var(--chrome-text) 8%, transparent);
	}
	.alerts-title {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.7rem;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: color-mix(in oklab, var(--chrome-text) 45%, transparent);
		margin: 0 0 0.75rem;
	}
	.alert-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.75rem;
		color: var(--chrome-text);
		margin-bottom: 0.4rem;
	}
	.alert-del {
		background: none;
		border: none;
		color: color-mix(in oklab, var(--chrome-text) 35%, transparent);
		cursor: pointer;
		font-size: 0.7rem;
		padding: 0;
	}
	.alert-del:hover { color: var(--mlb-red); }
	.alert-form {
		display: flex;
		gap: 0.35rem;
		margin-top: 0.75rem;
		flex-wrap: wrap;
	}
	.alert-select, .alert-input {
		background: color-mix(in oklab, var(--chrome-bg) 80%, transparent);
		border: 1px solid color-mix(in oklab, var(--chrome-text) 18%, transparent);
		border-radius: 0.25rem;
		color: var(--chrome-text);
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.72rem;
		padding: 0.3rem 0.5rem;
	}
	.alert-input { width: 5rem; }
	.alert-add {
		background: var(--mlb-red);
		border: none;
		border-radius: 0.25rem;
		color: #fff;
		cursor: pointer;
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.72rem;
		font-weight: 700;
		padding: 0.3rem 0.65rem;
	}
</style>
