<script lang="ts">
	import { onMount } from 'svelte';
	import FreshnessPanel from '$lib/components/board/FreshnessPanel.svelte';
	import { soundEnabled, setSoundEnabled } from '$lib/stores/sound';

	type SeasonMode = 'live' | 'between' | 'off-game' | 'off-season';
	type SeasonState = {
		mode: SeasonMode;
		gamesInProgress: number;
		updatedAt?: string;
	};
	type Freshness = {
		fresh: number;
		stale: number;
		old: number;
		total: number;
		updatedAt?: string;
	};

	const MODE_CLASS = {
		live: 'mode-live animate-pulse',
		between: 'mode-between',
		'off-game': 'mode-off-game',
		'off-season': 'mode-off-season'
	} as const;

	let seasonState = $state<SeasonState>({
		mode: 'off-season',
		gamesInProgress: 0
	});
	let freshness = $state<Freshness>({
		fresh: 0,
		stale: 0,
		old: 0,
		total: 0
	});
	let freshnessDebugOpen = $state(false);
	let loadError = $state('');

	const modeClass = $derived(MODE_CLASS[seasonState.mode]);
	const freshnessSummary = $derived(
		`${freshness.fresh} fresh · ${freshness.stale} stale · ${freshness.old} old`
	);
	const lastUpdatedText = $derived(
		(seasonState.updatedAt ?? freshness.updatedAt)
			? new Date(seasonState.updatedAt ?? freshness.updatedAt ?? '').toLocaleTimeString()
			: 'waiting for first sync'
	);

	function toggleSound() {
		setSoundEnabled(!$soundEnabled);
	}

	function toggleFreshnessDebug() {
		freshnessDebugOpen = !freshnessDebugOpen;
	}

	async function refreshStatus() {
		try {
			const seasonRes = await fetch('/api/season-state');
			const freshRes = await fetch('/api/freshness');

			if (seasonRes.ok) {
				const nextSeason = (await seasonRes.json()) as Partial<SeasonState>;
				seasonState = {
					mode: (nextSeason.mode as SeasonMode) ?? 'off-season',
					gamesInProgress: Number(nextSeason.gamesInProgress ?? 0),
					updatedAt: nextSeason.updatedAt
				};
			}

			if (freshRes.ok) {
				const nextFreshness = (await freshRes.json()) as Partial<Freshness>;
				freshness = {
					fresh: Number(nextFreshness.fresh ?? 0),
					stale: Number(nextFreshness.stale ?? 0),
					old: Number(nextFreshness.old ?? 0),
					total: Number(nextFreshness.total ?? 0),
					updatedAt: nextFreshness.updatedAt
				};
			}

			loadError = '';
		} catch (error) {
			loadError = error instanceof Error ? error.message : 'status unavailable';
		}
	}

	onMount(() => {
		void refreshStatus();
		const interval = window.setInterval(() => {
			void refreshStatus();
		}, 30000);
		return () => window.clearInterval(interval);
	});
</script>

<section class="board-header" aria-label="Board header">
	<h1>Diamond Departures</h1>
	<div class="status-row">
		<span class={`mode-pill ${modeClass}`}>{seasonState.mode}</span>
		<span class="status-pill">{seasonState.gamesInProgress} games live</span>
		<button class="status-pill button" type="button" onclick={toggleFreshnessDebug}>
			{freshnessSummary}
		</button>
		<span class="status-pill">Updated {lastUpdatedText}</span>
		<button class="status-pill button" type="button" onclick={toggleSound}>
			Sound {$soundEnabled ? 'on' : 'off'}
		</button>
	</div>

	{#if loadError}
		<p class="error">{loadError}</p>
	{/if}

	<FreshnessPanel open={freshnessDebugOpen} onclose={() => (freshnessDebugOpen = false)} />
</section>

<style>
	.board-header {
		display: grid;
		gap: 0.65rem;
		margin-bottom: 0.8rem;
	}

	h1 {
		margin: 0;
		font-family: 'Instrument Serif', serif;
		font-size: clamp(1.3rem, 3.2vw, 2rem);
	}

	.status-row {
		display: flex;
		flex-wrap: wrap;
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

	.button {
		cursor: pointer;
		color: inherit;
	}

	.mode-pill.mode-live {
		background: color-mix(in oklab, #14b8a6 40%, var(--chrome-bg));
	}

	.mode-pill.mode-between {
		background: color-mix(in oklab, #818cf8 35%, var(--chrome-bg));
	}

	.mode-pill.mode-off-game {
		background: color-mix(in oklab, #f59e0b 33%, var(--chrome-bg));
	}

	.mode-pill.mode-off-season {
		background: color-mix(in oklab, #94a3b8 30%, var(--chrome-bg));
	}

	.error {
		margin: 0;
		color: #fca5a5;
		font-size: 0.8rem;
	}

</style>
