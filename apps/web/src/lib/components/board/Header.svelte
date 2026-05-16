<script lang="ts">
	import { onMount } from 'svelte';
	import { soundEnabled, setSoundEnabled } from '$lib/stores/sound';
	import FreshnessPanel from '$lib/components/board/FreshnessPanel.svelte';

	type SeasonMode = 'live' | 'between' | 'off-game' | 'off-season';
	type SeasonState = {
		mode: SeasonMode;
		gamesInProgress: number;
		nextGameAt?: string;
		updatedAt?: string;
	};

	const MODE_CLASS = {
		live: 'mode-live animate-pulse',
		between: 'mode-between',
		'off-game': 'mode-off-game',
		'off-season': 'mode-off-season'
	} as const;

	let seasonState = $state<SeasonState>({ mode: 'off-season', gamesInProgress: 0 });
	let loadError = $state('');
	let showFreshnessDebug = $state(false);

	const modeClass = $derived(MODE_CLASS[seasonState.mode]);

	const idleHoursToNextGame = $derived(
		seasonState.nextGameAt
			? Math.max(0, Math.ceil((Date.parse(seasonState.nextGameAt) - Date.now()) / (1000 * 60 * 60)))
			: null
	);

	const idleBannerCopy = $derived(
		idleHoursToNextGame === null
			? 'No games today'
			: idleHoursToNextGame >= 24
				? 'No games today'
				: `No games until ${new Date(seasonState.nextGameAt ?? '').toLocaleTimeString()} · in ${idleHoursToNextGame} hours`
	);

	async function refreshStatus() {
		try {
			const seasonRes = await fetch('/api/season-state');
			if (seasonRes.ok) {
				const next = (await seasonRes.json()) as {
					mode?: SeasonMode;
					gamesInProgress?: number;
					next_game_at?: string;
				};
				seasonState = {
					mode: next.mode ?? 'off-season',
					gamesInProgress: Number(next.gamesInProgress ?? 0),
					nextGameAt: typeof next.next_game_at === 'string' ? next.next_game_at : undefined
				};
			}
			loadError = '';
			// Pre-warm freshness cache for debug panel; errors here are non-critical
			fetch('/api/freshness').catch(() => {});
		} catch (error) {
			loadError = error instanceof Error ? error.message : 'status unavailable';
		}
	}

	function toggleSound() {
		setSoundEnabled(!$soundEnabled);
	}

	function toggleFreshnessDebug() {
		showFreshnessDebug = !showFreshnessDebug;
	}

	onMount(() => {
		void refreshStatus();
		const interval = window.setInterval(() => void refreshStatus(), 30000);
		return () => window.clearInterval(interval);
	});
</script>

<div class="board-header">
	<div class="status-row">
		{#if seasonState.mode !== 'off-season'}
			<span class={`mode-pill ${modeClass}`}>{seasonState.mode}</span>
		{/if}

		{#if seasonState.mode === 'off-season'}
			<span class="status-pill off-season-banner">
				2025 regular season · final — next season starts soon
			</span>
		{:else if seasonState.mode === 'between' || seasonState.mode === 'off-game'}
			<span class="status-pill idle-banner">{idleBannerCopy}</span>
		{:else}
			<span class="status-pill">{seasonState.gamesInProgress} games live</span>
		{/if}

		<button class="icon-btn" type="button" aria-label="Toggle sound" onclick={toggleSound}>
			{$soundEnabled ? '🔊' : '🔇'}
		</button>

		<button class="icon-btn freshness-btn" type="button" aria-label="Show freshness debug panel" onclick={toggleFreshnessDebug}>
			⏱
		</button>
	</div>

	{#if showFreshnessDebug}
		<FreshnessPanel open={true} onclose={toggleFreshnessDebug} />
	{/if}

	{#if loadError}
		<p class="error">{loadError}</p>
	{/if}
</div>

<style>
	.board-header {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
		padding: 0.4rem 0.2rem;
	}

	.status-row {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 0.5rem;
	}

	.status-pill {
		padding: 0.35rem 0.65rem;
		border-radius: 999px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.73rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		background: color-mix(in oklab, var(--chrome-bg) 70%, black);
		border: 1px solid color-mix(in oklab, var(--chrome-text) 24%, transparent);
	}

	.mode-pill {
		padding: 0.35rem 0.65rem;
		border-radius: 999px;
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.73rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 24%, transparent);
	}

	.mode-pill.mode-live {
		background: var(--mlb-blue);
		color: white;
	}

	.mode-pill.mode-between {
		background: color-mix(in oklab, #818cf8 35%, var(--chrome-bg));
	}

	.mode-pill.mode-off-game {
		background: color-mix(in oklab, #f59e0b 33%, var(--chrome-bg));
	}

	.icon-btn {
		background: none;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 18%, transparent);
		border-radius: 0.3rem;
		padding: 0.25rem 0.45rem;
		cursor: pointer;
		font-size: 0.9rem;
		line-height: 1;
		color: var(--chrome-text);
	}

	.error {
		margin: 0;
		color: #fca5a5;
		font-size: 0.8rem;
	}
</style>
