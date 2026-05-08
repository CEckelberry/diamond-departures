# Packet P6-03 — Between-games and no-games-today states GREEN

## Goal
Implement Task 6.3 state handling while preserving board interactions.

## GREEN scope
- Header idle-state message for no live games and next game ETA.
- Board stream remains active in idle states with slower reconnect/heartbeat policy.
- Stat picker and board sorting still functional.

## Acceptance
- P6-03 tests pass.
- Existing Phase 4-6 web tests stay green.



## Task 6.3 spec excerpt

## Task 6.3 — Between-games and no-games-today states

**Goal.** Handle the in-season-but-no-current-games state gracefully.

**Outputs.**

- Header banner shows "No games until [next game] · in [N hours]" when no games are live
- SSE still opens (in case a game starts) but at a slower heartbeat (2 minutes)
- Stat picker still works for re-sorting

**Acceptance criteria.**

- A day with no scheduled games shows the appropriate banner
- A day with games but none currently live shows the "next game in" banner
- When a game starts, the banner switches automatically to "live" within 60 seconds

---

# Phase 7 — Polish + case study

Goal: the site is fast, accessible, and feels finished. Case study written. Public launch.

- [ ] Task 7.1 — Performance pass
- [ ] Task 7.2 — Accessibility pass
- [ ] Task 7.3 — Mobile experience
- [ ] Task 7.4 — SEO + Open Graph
- [ ] Task 7.5 — Methodology page
- [ ] Task 7.6 — Write the case study
- [ ] Task 7.7 — Launch

---

## Task 7.1 — Performance pass

**Goal.** The board renders smoothly during high-activity moments (multiple games live, many concurrent deltas).

**Outputs.**

- A Playwright perf script that simulates a busy ingest period
- Optimization of the flap animation to use compositor-only transforms
- Lazy loading of player detail content
- Image optimization for headshots

**Acceptance criteria.**

- 60fps maintained during a 50-cell simultaneous flap (verify in Performance tab)
- Lighthouse Performance ≥ 90 on desktop and ≥ 80 on mobile (mobile is harder due to animation)
- Initial board render under 1.5s on a fast connection
- INP under 200ms for stat-picker switches (the highest-load interaction)

---

## Task 7.2 — Accessibility pass

**Goal.** Lighthouse Accessibility 100. Site usable with screen reader.

**Outputs.**

-


## Current Header.svelte

<script lang="ts">
	import { onMount } from 'svelte';
	import FreshnessPanel from '$lib/components/board/FreshnessPanel.svelte';
	import { soundEnabled, setSoundEnabled } from '$lib/stores/sound';

	type SeasonMode = 'live' | 'between' | 'off-game' | 'off-season';
	type SeasonState = {
		mode: SeasonMode;
		gamesInProgress: number;
		currentSeason?: number;
		nextSeasonStartsAt?: string;
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

	let {
		previewRunning = false,
		onTogglePreview
	}: {
		previewRunning?: boolean;
		onTogglePreview?: () => void;
	} = $props();

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
	const offSeasonYear = $derived(seasonState.currentSeason ?? new Date().getFullYear());
	const nextSeasonCountdown = $derived(
		seasonState.nextSeasonStartsAt
			? `next season ${new Date(seasonState.nextSeasonStartsAt).toLocaleDateString()}`
			: 'next season pending schedule'
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
				const nextSeason = (await seasonRes.json()) as {
					mode?: SeasonMode;
					gamesInProgress?: number;
					updatedAt?: string;
					current_season?: number;
					next_game_at?: string;
				};
				seasonState = {
					mode: nextSeason.mode ?? 'off-season',
					gamesInProgress: Number(nextSeason.gamesInProgress ?? 0),
					currentSeason:
						typeof nextSeason.current_season === 'number'
							? nextSeason.current_season
							: undefined,
					nextSeasonStartsAt:
						typeof nextSeason.next_game_at === 'string' ? nextSeason.next_game_at : undefined,
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
		{#if seasonState.mode === 'off-season'}
			<span class="status-pill off-season-banner">{offSeasonYear} regular season · final</span>
			<span class="status-pill">{nextSeasonCountdown}</span>
			<button class="status-pill button" type="button" onclick={onTogglePreview}>
				{previewRunning ? 'Exit preview mode' : 'Preview mode'}
			</button>
			{#if previewRunning}
				<span class="status-pill preview-running">Preview running · replay mode</span>
			{/if}
		{:else}
			<span class="status-pill">{seasonState.gamesInProgress} games live</span>
		{/if}
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



## Current +page.svelte

<script lang="ts">
	import { onMount } from 'svelte';
	import { navigating, page } from '$app/stores';
	import Header from '$lib/components/board/Header.svelte';
	import ViewTabs from '$lib/components/board/ViewTabs.svelte';
	import StatPicker from '$lib/components/board/StatPicker.svelte';
	import Board from '$lib/components/board/Board.svelte';
	import Panel from '$lib/components/player/Panel.svelte';
	import { openBoardStream } from '$lib/api/sse';
	import { applyDelta, applySnapshot, boardRows as boardRowsStore, seedBoard } from '$lib/stores/board';

	type SeasonMode = 'live' | 'between' | 'off-game' | 'off-season';

	type BoardEntryPayload = {
		rank: number;
		player: {
			id: number;
			name: string;
			team_abbr: string;
			headshot_url: string;
			position: string;
		};
		stat_value: number;
		freshness: {
			timestamp: string;
			age_category: 'live' | 'recent' | 'stale' | 'old';
		};
	};

	let {
		data
	}: {
		data: {
			boardView: string;
			boardSort: string;
			entries: BoardEntryPayload[];
			selectedPosition: string;
		};
	} = $props();

	const view = $derived($page.url.searchParams.get('view') ?? 'hitters');
	const isLoading = $derived($navigating !== null);
	const boardRows = $derived($boardRowsStore);
	const selectedPosition = $derived(data.selectedPosition);
	const filteredRows = $derived(
		(() => {
			if (view !== 'positions' || !selectedPosition || selectedPosition === 'all') {
				return boardRows;
			}
			return boardRows.filter((row) => row.position === selectedPosition);
		})()
	);

	let selectedPlayerId = $state<number | null>(null);
	let seasonMode = $state<SeasonMode>('off-season');
	let previewMode = $state(false);
	let stop = () => {};

	function handleSelectPlayer(playerId: number) {
		selectedPlayerId = playerId;
	}

	function togglePreviewMode() {
		previewMode = !previewMode;
	}

	async function refreshSeasonMode() {
		try {
			const response = await fetch('/api/season-state');
			if (!response.ok) return;
			const payload = (await response.json()) as { mode?: SeasonMode };
			seasonMode = payload.mode ?? 'off-season';
		} catch {
			seasonMode = 'off-season';
		}
	}

	onMount(() => {
		void refreshSeasonMode();
		const interval = window.setInterval(() => {
			void refreshSeasonMode();
		}, 30000);
		return () => {
			stop();
			window.clearInterval(interval);
		};
	});

	$effect(() => {
		seedBoard(data.boardView, data.boardSort, data.entries);
		selectedPlayerId = data.entries[0]?.player.id ?? null;
		stop();
		if (seasonMode === 'off-season' && !previewMode) return;
		const endpoint = previewMode ? '/api/board/preview-sse' : '/api/board/sse';
		stop = openBoardStream(
			data.boardView,
			data.boardSort,
			{
				onSnapshot: (payload) => applySnapshot(payload),
				onDelta: (payload) => applyDelta(payload)
			},
			{ endpoint }
		);
	});
</script>

<section class="board-screen">
	<Header previewRunning={previewMode} onTogglePreview={togglePreviewMode} />
	{#if previewMode}
		<p class="preview-label" aria-live="polite">preview running · Replay mode</p>
	{/if}
	<div class="controls">
		<ViewTabs />
		<StatPicker {view} />
	</div>

	<div class="board-layout">
		{#if isLoading}
			<div class="board-skeleton" aria-label="Loading board">
				<div class="skeleton-row"></div>
				<div class="skeleton-row"></div>
				<div class="skeleton-row"></div>
				<div class="skeleton-row"></div>
			</div>
		{:else}
			<Board rows={filteredRows} onselect={handleSelectPlayer} />
		{/if}
		<Panel selectedPlayerId={selectedPlayerId} />
	</div>
</section>

<style>
	.board-screen {
		display: grid;
		gap: 0.8rem;
	}

	.preview-label {
		margin: 0;
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.68rem;
		text-transform: uppercase;
		letter-spacing: 0.07em;
		color: color-mix(in oklab, #fcd34d 80%, var(--chrome-text));
	}

	.controls {
		display: grid;
		gap: 0.5rem;
	}

	.board-layout {
		display: grid;
		gap: 0.7rem;
		grid-template-columns: minmax(0, 1fr) minmax(240px, 300px);
		align-items: start;
	}

	.board-skeleton {
		display: grid;
		gap: 0.35rem;
		padding: 0.8rem;
		border-radius: 0.6rem;
		background: color-mix(in oklab, var(--board-bg) 90%, black);
		border: 1px solid color-mix(in oklab, var(--chrome-text) 14%, transparent);
	}

	.skeleton-row {
		height: 36px;
		border-radius: 0.35rem;
		background: linear-gradient(
			90deg,
			color-mix(in oklab, var(--chrome-bg) 60%, transparent) 25%,
			color-mix(in oklab, var(--chrome-bg) 30%, white) 50%,
			color-mix(in oklab, var(--chrome-bg) 60%, transparent) 75%
		);
		background-size: 220% 100%;
		animation: board-skeleton-slide 1.1s ease-in-out infinite;
	}

	@keyframes board-skeleton-slide {
		0% {
			background-position: 120% 0;
		}
		100% {
			background-position: -120% 0;
		}
	}

	@media (max-width: 1140px) {
		.board-layout {
			grid-template-columns: 1fr;
		}
	}
</style>



## Current SSE client

type SnapshotPayload = {
	view: string;
	sort: string;
	entries: Array<{
		rank: number;
		player: {
			id: number;
			name: string;
			team_abbr: string;
			headshot_url: string;
			position: string;
		};
		stat_value: number;
		freshness: {
			timestamp: string;
			age_category: "live" | "recent" | "stale" | "old";
		};
	}>;
};

type DeltaPayload = {
	view: string;
	sort: string;
	changes: Array<{
		player_id: number;
		old_rank: number | null;
		new_rank: number | null;
		changed_stats: Array<{ name: string; old: unknown; new: unknown }>;
	}>;
};

type StreamHandlers = {
	onSnapshot: (payload: SnapshotPayload) => void;
	onDelta: (payload: DeltaPayload) => void;
	onError?: (error: Event) => void;
};

type StreamOptions = {
	endpoint?: string;
};

export function openBoardStream(
	view: string,
	sort: string,
	handlers: StreamHandlers,
	options?: StreamOptions,
): () => void {
	if (typeof window === "undefined") {
		return () => {};
	}

	let stopped = false;
	let attempts = 0;
	let retryTimer: number | null = null;
	let source: EventSource | null = null;

	const connect = () => {
		if (stopped) return;
		const params = new URLSearchParams();
		params.set("view", view);
		params.set("sort", sort);
		if (!options?.endpoint) {
			source = new EventSource("/api/board/sse?" + params.toString());
		} else {
			source = new EventSource(options.endpoint + "?" + params.toString());
		}

		source.addEventListener("snapshot", (event) => {
			attempts = 0;
			handlers.onSnapshot(
				JSON.parse((event as MessageEvent).data) as SnapshotPayload,
			);
		});

		source.addEventListener("delta", (event) => {
			handlers.onDelta(
				JSON.parse((event as MessageEvent).data) as DeltaPayload,
			);
		});

		source.onerror = (event) => {
			handlers.onError?.(event);
			source?.close();
			if (stopped) return;
			const delay = Math.min(8000, 500 * 2 ** attempts);
			attempts += 1;
			retryTimer = window.setTimeout(connect, delay);
		};
	};

	connect();

	return () => {
		stopped = true;
		if (retryTimer !== null) window.clearTimeout(retryTimer);
		source?.close();
	};
}
