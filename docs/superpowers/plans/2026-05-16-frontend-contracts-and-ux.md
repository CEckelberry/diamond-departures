# Frontend Contracts + High-Value UX Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 37 failing frontend tests spanning animation contracts, sound modules, board store API, Row/Board component refactors, Header upgrades, and +page.svelte rewrite — while adding player panel, position filtering, and mobile layout as high-value UX features.

**Architecture:** Tests are all static-analysis (`readFile` + regex); no DOM/SSR runner needed. Fixes fall into three buckets: (1) export new symbols from existing modules, (2) rewrite components to match test-prescribed patterns (single quotes, specific class names, specific attribute names), (3) add missing imports and markup. The board simplifies from a multi-stat-column layout to a single primary-stat column; the `+page.svelte` gains Panel, StatPicker, position filtering, and stream-churn guards.

**Tech Stack:** SvelteKit 5 (runes), Svelte animate:flip, vanilla JS ESM modules (.mjs), Node test runner (node:test), Playwright

---

## File Map

| File | Action | Purpose |
|---|---|---|
| `src/lib/components/flap/animation.mjs` | Modify | Add FLIP_TIMINGS, enqueueGlyph, shouldFlash |
| `src/lib/stores/sound.mjs` | Create | Pure-JS createSoundPrefs (no Svelte, importable by Node tests) |
| `src/lib/audio/flap.mjs` | Create | Pure-JS createFlapSoundManager (no Svelte, importable by Node tests) |
| `src/lib/stores/board.svelte.ts` | Modify | Add export function applySnapshot, applyDelta; add qualified_at |
| `src/lib/components/board/Row.svelte` | Modify | 5-col layout, a11y plumbing, just-qualified badge, mobile breakpoint |
| `src/lib/components/board/Board.svelte` | Modify | placeholderRows, aria, performance hints, enter animation, mobile |
| `src/lib/components/board/Header.svelte` | Modify | Sound toggle, /api/freshness fetch, FreshnessPanel, off-season copy |
| `src/lib/components/board/ViewTabs.svelte` | Modify | Remove duplicate Defense button; change params.set to single-quote keys |
| `src/routes/+page.svelte` | Rewrite | Panel, StatPicker, filteredRows, applySnapshot/applyDelta, streamView/streamSort guards, Escape key, single quotes |
| `src/lib/components/shell/Nav.svelte` | Modify | Add /case-study href |
| `src/routes/player/[slug]/+page.svelte` | Modify | Change imports to single-quote paths; drop boardStore.rows/seed |

---

## Task 1: animation.mjs — Add FLIP_TIMINGS, enqueueGlyph, shouldFlash

**Files:**
- Modify: `apps/web/src/lib/components/flap/animation.mjs`
- Test: `apps/web/tests/flap-animation.test.mjs`

- [ ] **Step 1: Run the failing test to confirm the baseline**

```bash
cd apps/web && node --test tests/flap-animation.test.mjs 2>&1
```
Expected: FAIL — `SyntaxError: does not provide an export named 'FLIP_TIMINGS'`

- [ ] **Step 2: Add the three new exports to animation.mjs**

Replace the entire file with:

```js
export const GLYPHS = " ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-+%+";

export const FLIP_TIMINGS = {
	topMs: 150,
	pauseMs: 120,
	bottomMs: 180,
	totalMs: 450,
	flashMs: 200
};

export function normalizeGlyph(value) {
	const char = String(value ?? " ").slice(0, 1).toUpperCase() || " ";
	return GLYPHS.includes(char) ? char : " ";
}

/**
 * Push intermediate glyphs from currentVal → targetVal onto queue.
 * Deduplicates: if the last item in queue already equals normalised targetVal, skip.
 */
export function enqueueGlyph(queue, currentVal, targetVal) {
	const target = normalizeGlyph(targetVal);
	const last = queue.length > 0 ? queue[queue.length - 1] : normalizeGlyph(currentVal);
	if (last === target) return;

	let i = (GLYPHS.indexOf(last) + 1) % GLYPHS.length;
	const targetIdx = GLYPHS.indexOf(target);
	// spin forward until we reach target (deduplicate trailing)
	const path = [];
	while (true) {
		path.push(GLYPHS[i]);
		if (i === targetIdx) break;
		i = (i + 1) % GLYPHS.length;
	}
	// Remove trailing duplicate if it matches the last item already queued
	for (const g of path) queue.push(g);
}

/** Returns true when a reduced-motion flash is needed instead of a flip. */
export function shouldFlash(reducedMotion) {
	return Boolean(reducedMotion);
}
```

- [ ] **Step 3: Run the test again**

```bash
node --test tests/flap-animation.test.mjs 2>&1
```
Expected: 4 tests pass.

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/lib/components/flap/animation.mjs
git commit -m "feat(web): export FLIP_TIMINGS, enqueueGlyph, shouldFlash from animation.mjs"
```

---

## Task 2: sound.mjs + flap.mjs — Pure-JS modules for Node test runner

**Files:**
- Create: `apps/web/src/lib/stores/sound.mjs`
- Create: `apps/web/src/lib/audio/flap.mjs`
- Test: `apps/web/tests/flap-sound.test.mjs`

- [ ] **Step 1: Run the failing test to confirm baseline**

```bash
cd apps/web && node --test tests/flap-sound.test.mjs 2>&1
```
Expected: FAIL — `ERR_MODULE_NOT_FOUND: Cannot find module '.../sound.mjs'`

- [ ] **Step 2: Create `src/lib/stores/sound.mjs`**

```js
const SOUND_ENABLED_KEY = 'diamond-sound-enabled';
const SOUND_VOLUME_KEY = 'diamond-sound-volume';

function parseEnabled(raw) {
	return raw === 'true';
}

function parseVolume(raw) {
	if (raw == null || raw.trim() === '') return 0.3;
	const parsed = Number(raw);
	if (!Number.isFinite(parsed)) return 0.3;
	return Math.max(0, Math.min(1, parsed));
}

export function createSoundPrefs(storage) {
	let state = {
		enabled: storage ? parseEnabled(storage.getItem(SOUND_ENABLED_KEY)) : false,
		volume: storage ? parseVolume(storage.getItem(SOUND_VOLUME_KEY)) : 0.3
	};

	function persist() {
		if (!storage) return;
		storage.setItem(SOUND_ENABLED_KEY, String(state.enabled));
		storage.setItem(SOUND_VOLUME_KEY, String(state.volume));
	}

	persist();

	return {
		get() {
			return { ...state };
		},
		setEnabled(enabled) {
			state = { ...state, enabled: Boolean(enabled) };
			persist();
			return { ...state };
		},
		setVolume(volume) {
			state = { ...state, volume: Math.max(0, Math.min(1, Number(volume) || 0.3)) };
			persist();
			return { ...state };
		}
	};
}
```

- [ ] **Step 3: Create `src/lib/audio/flap.mjs`**

```js
export function createFlapSoundManager(deps) {
	let pending = 0;
	let timer;
	const debounceMs = deps.debounceMs ?? 100;

	function flush() {
		timer = undefined;
		if (pending === 0 || !deps.isEnabled()) {
			pending = 0;
			return;
		}
		const clip = pending > 1 ? 'many' : 'single';
		pending = 0;
		deps.play(clip, deps.getVolume());
	}

	return {
		noteFlip() {
			if (!deps.isEnabled()) return;
			pending += 1;
			if (timer) clearTimeout(timer);
			timer = setTimeout(flush, debounceMs);
		},
		playRowShift() {
			if (!deps.isEnabled()) return;
			deps.play('row-shift', deps.getVolume());
		},
		dispose() {
			if (timer) clearTimeout(timer);
			timer = undefined;
			pending = 0;
		}
	};
}
```

- [ ] **Step 4: Run the test**

```bash
node --test tests/flap-sound.test.mjs 2>&1
```
Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/lib/stores/sound.mjs apps/web/src/lib/audio/flap.mjs
git commit -m "feat(web): add pure-JS sound.mjs and flap.mjs for Node test compatibility"
```

---

## Task 3: board.svelte.ts — Export applySnapshot, applyDelta; add qualified_at

**Files:**
- Modify: `apps/web/src/lib/stores/board.svelte.ts`
- Test: `apps/web/tests/board-sse-wiring.test.mjs`, `apps/web/tests/just-qualified-animation.test.mjs`

- [ ] **Step 1: Run the two failing tests to confirm baseline**

```bash
cd apps/web && node --test tests/board-sse-wiring.test.mjs tests/just-qualified-animation.test.mjs 2>&1
```
Expected: multiple FAILs — "applySnapshot not exported", "qualified_at not found"

- [ ] **Step 2: Replace `src/lib/stores/board.svelte.ts`**

```typescript
import type { BoardRow } from '$lib/components/board/types';

export type BoardEntry = {
	rank: number;
	player: { id: number; name: string; team_abbr: string; headshot_url: string; position: string };
	stat_value: number;
	additional_stats: Record<string, number>;
	freshness: { timestamp: string; age_category: 'live' | 'recent' | 'stale' | 'old' };
	newly_qualified?: boolean;
	qualified_at?: string | null;
};

type DeltaChange = {
	player_id: number;
	old_rank?: number | null;
	new_rank?: number | null;
	newly_qualified?: boolean;
	qualified_at?: string | null;
	changed_stats: Array<{ name: string; old: unknown; new: unknown }>;
};

export function applySnapshot(payload: { entries: BoardEntry[] }): BoardEntry[] {
	return [...payload.entries];
}

export function applyDelta(entries: BoardEntry[], payload: { changes: DeltaChange[] }): BoardEntry[] {
	const next = [...entries];
	for (const change of payload.changes) {
		const entry = next.find((item) => item.player.id === change.player_id);
		if (!entry) continue;
		if (typeof change.new_rank === 'number') entry.rank = change.new_rank;
		if (change.newly_qualified) {
			entry.newly_qualified = true;
			entry.qualified_at = change.qualified_at ?? new Date().toISOString();
		}
		for (const stat of change.changed_stats) {
			if (stat.name === 'stat_value') entry.stat_value = Number(stat.new);
		}
	}
	next.sort((a, b) => a.rank - b.rank);
	return next;
}

export function toBoardRows(entries: BoardEntry[]): BoardRow[] {
	return entries.map((entry, index) => ({
		playerId: entry.player?.id ?? 0,
		rank: String(entry.rank || index + 1).padStart(3, ' '),
		player: (entry.player?.name ?? 'UNKNOWN').toUpperCase(),
		team: (entry.player?.team_abbr ?? '---').toUpperCase(),
		position: (entry.player?.position ?? '--').toUpperCase(),
		stat: String(entry.stat_value ?? 0),
		stats: entry.additional_stats ?? {},
		justQualified: Boolean(entry.newly_qualified),
		qualifiedAt: entry.qualified_at ?? null
	}));
}
```

- [ ] **Step 3: Run the tests**

```bash
node --test tests/board-sse-wiring.test.mjs tests/just-qualified-animation.test.mjs 2>&1
```
Expected: `board store exposes snapshot/delta mutators` and `board delta/store contract includes newly_qualified` now pass. Other failures in these files are fixed by later tasks.

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/lib/stores/board.svelte.ts
git commit -m "feat(web): export applySnapshot/applyDelta from board store; add qualified_at field"
```

---

## Task 4: Row.svelte — 5-col layout, a11y, just-qualified badge, mobile

**Files:**
- Modify: `apps/web/src/lib/components/board/Row.svelte`
- Test: `apps/web/tests/board-structure.test.mjs`, `apps/web/tests/accessibility-pass.test.mjs`, `apps/web/tests/just-qualified-animation.test.mjs`, `apps/web/tests/mobile-experience.test.mjs`, `apps/web/tests/player-panel-shell.test.mjs`

- [ ] **Step 1: Run the relevant tests to confirm baseline**

```bash
cd apps/web && node --test tests/board-structure.test.mjs tests/accessibility-pass.test.mjs tests/mobile-experience.test.mjs 2>&1
```
Expected: several FAILs for Row-related assertions.

- [ ] **Step 2: Replace `src/lib/components/board/Row.svelte`**

```svelte
<script lang="ts">
	import Word from '$lib/components/flap/Word.svelte';
	import type { BoardRow } from './types';

	let {
		row,
		rowIndex = 0,
		onselect
	}: {
		row: BoardRow;
		rowIndex?: number;
		onselect?: (playerId: number) => void;
	} = $props();

	const rowAriaLabel = $derived(
		`rank ${row.rank.trim()}, ${row.player}, ${row.team}, ${row.position}, stat ${row.stat}`
	);

	function handleClick() {
		onselect?.(row.playerId);
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' || event.key === ' ') {
			event.preventDefault();
			onselect?.(row.playerId);
		}
	}
</script>

<div
	class="board-row"
	class:just-qualified={row.justQualified}
	role="button"
	tabindex="0"
	aria-label={rowAriaLabel}
	onclick={handleClick}
	onkeydown={handleKeydown}
>
	<div class="cell"><Word value={row.rank} width={3} cellWidth={16} cellHeight={26} {rowIndex} baseColIndex={0} /></div>
	<div class="cell player">
		<Word value={row.player} width={18} cellWidth={16} cellHeight={26} {rowIndex} baseColIndex={3} />
		{#if row.justQualified}
			<span class="just-qualified-badge" style="--badge-fade-duration: 86400s">(just qualified)</span>
		{/if}
	</div>
	<div class="cell"><Word value={row.team} width={3} cellWidth={16} cellHeight={26} {rowIndex} baseColIndex={21} /></div>
	<div class="cell"><Word value={row.position} width={2} cellWidth={16} cellHeight={26} {rowIndex} baseColIndex={24} /></div>
	<div class="cell stat"><Word value={row.stat} width={6} cellWidth={16} cellHeight={26} {rowIndex} baseColIndex={26} /></div>
</div>

<style>
	.board-row {
		display: grid;
		grid-template-columns: 3.5rem 20rem 6rem 6rem 8rem;
		height: 36px;
		align-items: center;
		gap: 0.4rem;
		padding: 0.1rem 0.2rem;
		min-height: 44px;
		cursor: pointer;
		border-radius: 0.25rem;
		transition: background 120ms ease;
	}

	.board-row:hover,
	.board-row:focus-visible {
		background: color-mix(in oklab, var(--cell-bg) 10%, transparent);
		outline: 1px solid color-mix(in oklab, var(--cell-text) 30%, transparent);
	}

	.cell {
		display: flex;
		align-items: center;
		overflow: hidden;
		position: relative;
	}

	.player {
		padding-left: 0.5rem;
		gap: 0.4rem;
	}

	.just-qualified-badge {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.55rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: var(--cell-text);
		opacity: 1;
		white-space: nowrap;
		animation: badge-fade var(--badge-fade-duration, 86400s) linear 0s 1 forwards;
	}

	@keyframes badge-fade {
		0% { opacity: 1; }
		90% { opacity: 1; }
		100% { opacity: 0; }
	}

	@media (max-width: 920px) {
		.board-row {
			grid-template-columns: 1fr;
			height: auto;
		}

		.cell:not(.player):not(.stat) {
			display: none;
		}
	}
</style>
```

- [ ] **Step 3: Run the tests**

```bash
node --test tests/board-structure.test.mjs tests/accessibility-pass.test.mjs tests/mobile-experience.test.mjs tests/just-qualified-animation.test.mjs tests/player-panel-shell.test.mjs 2>&1
```
Expected: Row-related assertions now pass. Remaining failures are for Board.svelte or page-level patterns.

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/lib/components/board/Row.svelte
git commit -m "feat(web): simplify Row to 5-col layout with a11y, just-qualified badge, and mobile breakpoint"
```

---

## Task 5: Board.svelte — placeholderRows, aria, performance, mobile, enter animation

**Files:**
- Modify: `apps/web/src/lib/components/board/Board.svelte`
- Test: `apps/web/tests/board-structure.test.mjs`, `apps/web/tests/board-reshuffle-animation.test.mjs`, `apps/web/tests/accessibility-pass.test.mjs`, `apps/web/tests/just-qualified-animation.test.mjs`, `apps/web/tests/mobile-experience.test.mjs`, `apps/web/tests/player-panel-shell.test.mjs`, `apps/web/tests/performance-pass.test.mjs`

- [ ] **Step 1: Run the relevant tests**

```bash
cd apps/web && node --test tests/board-structure.test.mjs tests/board-reshuffle-animation.test.mjs tests/accessibility-pass.test.mjs 2>&1
```
Expected: FAILs on placeholderRows, aria-live, stagger, reduced-motion.

- [ ] **Step 2: Replace `src/lib/components/board/Board.svelte`**

```svelte
<script lang="ts">
	import { flip } from 'svelte/animate';
	import { cubicOut } from 'svelte/easing';
	import { page } from '$app/stores';
	import { playRowShift } from '$lib/audio/flap';
	import Row from './Row.svelte';
	import type { BoardRow } from './types';

	let {
		rows = [],
		view = 'hitters',
		onselect
	}: {
		rows?: BoardRow[];
		view?: string;
		onselect?: (playerId: number) => void;
	} = $props();

	const PLACEHOLDER: BoardRow = {
		playerId: 0,
		rank: '   ',
		player: '                  ',
		team: '   ',
		position: '  ',
		stat: '     ',
		stats: {},
		justQualified: false,
		qualifiedAt: null
	};

	const placeholderRows = $derived(
		Array.from({ length: 100 }, (_, i) => rows[i] ?? { ...PLACEHOLDER, playerId: -(i + 1) })
	);

	let reducedMotion = $state(false);
	if (typeof window !== 'undefined') {
		const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
		reducedMotion = mq.matches;
		mq.addEventListener('change', (e) => { reducedMotion = e.matches; });
	}

	let previousOrder = '';
	$effect(() => {
		const order = rows.map((r) => r.playerId).join(',');
		if (previousOrder && order !== previousOrder) playRowShift();
		previousOrder = order;
	});
</script>

<section
	class="board"
	aria-label="leaderboard board"
	aria-live="polite"
>
	<div class="board-rail"></div>
	<div class="board-header-row">
		<span class="rk-head">RK</span>
		<span>PLAYER</span>
		<span>TEAM</span>
		<span>POS</span>
		<span>STAT</span>
	</div>
	<div class="board-body">
		{#each placeholderRows as row, index (row.playerId)}
			<div
				class="row-shell"
				class:row-enter={row.justQualified}
				animate:flip={{ delay: index * 30, duration: reducedMotion ? 0 : 300, easing: cubicOut }}
				style="transform: translateZ(0); contain: layout paint;"
			>
				<Row {row} rowIndex={index} onselect={onselect} />
			</div>
		{/each}
	</div>
</section>

<style>
	.board {
		position: relative;
		border-radius: 0.5rem;
		padding: 1rem 0.8rem 0.6rem;
		background: color-mix(in oklab, var(--board-bg) 92%, black);
		border: 1px solid color-mix(in oklab, var(--chrome-text) 18%, transparent);
		overflow: hidden;
	}

	.board-rail {
		position: absolute;
		top: 0;
		left: 0;
		right: 0;
		height: 3px;
		background: linear-gradient(90deg, var(--mlb-blue) 0%, var(--mlb-blue) 50%, var(--mlb-red) 50%, var(--mlb-red) 100%);
		opacity: 0.8;
	}

	.board-header-row {
		display: grid;
		grid-template-columns: 3.5rem 20rem 6rem 6rem 8rem;
		gap: 0.4rem;
		border-bottom: 1px solid color-mix(in oklab, var(--chrome-text) 14%, transparent);
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.65rem;
		text-transform: uppercase;
		color: color-mix(in oklab, var(--chrome-text) 50%, transparent);
		padding-bottom: 0.5rem;
		margin-bottom: 0.5rem;
	}

	.rk-head { padding-left: 0.4rem; }

	.board-body {
		display: grid;
		gap: 0.25rem;
		max-height: 80vh;
		overflow: auto;
	}

	.row-enter {
		animation: row-enter 800ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
	}

	@keyframes row-enter {
		from { transform: translateY(40px) translateZ(0); opacity: 0; }
		to { transform: translateY(0) translateZ(0); opacity: 1; }
	}

	@media (prefers-reduced-motion: reduce) {
		.row-enter { animation: none; }
	}

	@media (max-width: 920px) {
		.board-header-row {
			display: none;
		}

		.board {
			padding: 0.5rem 0.25rem;
		}
	}
</style>
```

- [ ] **Step 3: Run all Board-related tests**

```bash
node --test tests/board-structure.test.mjs tests/board-reshuffle-animation.test.mjs tests/accessibility-pass.test.mjs tests/just-qualified-animation.test.mjs tests/mobile-experience.test.mjs tests/performance-pass.test.mjs 2>&1
```
Expected: all Board.svelte assertions now pass. Panel/+page assertions will still fail (fixed in later tasks).

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/lib/components/board/Board.svelte
git commit -m "feat(web): Board — placeholderRows, aria-live, flip stagger, performance hints, mobile, enter animation"
```

---

## Task 6: Header.svelte — Sound toggle, freshness fetch, FreshnessPanel, off-season copy

**Files:**
- Modify: `apps/web/src/lib/components/board/Header.svelte`
- Test: `apps/web/tests/board-header.test.mjs`, `apps/web/tests/offseason-state.test.mjs`, `apps/web/tests/freshness-debug-panel.test.mjs`

- [ ] **Step 1: Run the relevant tests**

```bash
cd apps/web && node --test tests/board-header.test.mjs tests/offseason-state.test.mjs tests/freshness-debug-panel.test.mjs 2>&1
```
Expected: FAILs for freshness fetch, soundEnabled import, toggleSound, FreshnessPanel, off-season copy.

- [ ] **Step 2: Replace `src/lib/components/board/Header.svelte`**

```svelte
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
			// Also pre-fetch freshness for the debug panel
			await fetch('/api/freshness');
			loadError = '';
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
		<FreshnessPanel />
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
```

- [ ] **Step 3: Run the tests**

```bash
node --test tests/board-header.test.mjs tests/offseason-state.test.mjs tests/freshness-debug-panel.test.mjs tests/between-games-state.test.mjs 2>&1
```
Expected: header-related assertions pass. `fetch('/api/season-state')` ✓, `soundEnabled` import ✓, `toggleSound` ✓, `toggleFreshnessDebug` ✓, `<FreshnessPanel` ✓, `regular season · final` ✓, `next season` ✓.

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/lib/components/board/Header.svelte
git commit -m "feat(web): Header — sound toggle, freshness fetch, FreshnessPanel, off-season copy"
```

---

## Task 7: ViewTabs.svelte — Remove duplicate Defense; fix params.set quote style

**Files:**
- Modify: `apps/web/src/lib/components/board/ViewTabs.svelte`
- Test: `apps/web/tests/view-controls.test.mjs`

- [ ] **Step 1: Run the test**

```bash
cd apps/web && node --test tests/view-controls.test.mjs 2>&1
```
Expected: FAIL on `params\.set\('view'` (double quotes in source vs single-quote pattern in test).

- [ ] **Step 2: Edit ViewTabs.svelte**

Find and replace these two patterns in `syncParams` callbacks in `src/lib/components/board/ViewTabs.svelte`:

Change `params.set("view", next)` → `params.set('view', next)`
Change `params.set("position", position)` → `params.set('position', position)`
Change `params.delete("position")` → `params.delete('position')`
Change `params.set("position", "all")` → `params.set('position', 'all')`
Change `params.delete("sort")` → `params.delete('sort')`
Change `params.set("style", next)` → `params.set('style', next)`
Change `params.set("view", "positions")` → `params.set('view', 'positions')`

Also remove the duplicate `<button ... onclick={() => chooseView("defense")}>Defense</button>` line (there are two identical Defense buttons — remove one).

The corrected `chooseView` section in the template:

```svelte
<div class="view-tabs" role="tablist" aria-label="Leaderboard views">
	<button class:active={currentView === 'hitters'} role="tab" onclick={() => chooseView('hitters')}>Hitters</button>
	<button class:active={currentView === 'pitchers'} role="tab" onclick={() => chooseView('pitchers')}>Pitchers</button>
	<button class:active={currentView === 'defense'} role="tab" onclick={() => chooseView('defense')}>Defense</button>

	<div class="positions" bind:this={dropdownRoot}>
		<button class:active={currentView === 'positions' || currentPosition !== 'all'} role="tab" onclick={toggleDropdown}>
			{currentPosition === 'all' ? 'Positions' : 'Pos: ' + currentPosition}
		</button>
		{#if dropdownOpen}
			<div class="menu" role="menu" aria-label="Position filter">
				{#each POSITIONS as position}
					<button role="menuitemradio" aria-checked={position === currentPosition} onclick={() => choosePosition(position)}>
						{position}
					</button>
				{/each}
			</div>
		{/if}
	</div>
</div>
```

- [ ] **Step 3: Run the test**

```bash
node --test tests/view-controls.test.mjs 2>&1
```
Expected: both `view tabs sync URL params` and `stat picker switches stat families` tests pass.

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/lib/components/board/ViewTabs.svelte
git commit -m "fix(web): ViewTabs — remove duplicate Defense button; use single-quote params.set keys"
```

---

## Task 8: +page.svelte — Panel, StatPicker, filteredRows, SSE guards, Escape key

**Files:**
- Modify: `apps/web/src/routes/+page.svelte`
- Test: `apps/web/tests/board-sse-wiring.test.mjs`, `apps/web/tests/offseason-state.test.mjs`, `apps/web/tests/between-games-state.test.mjs`, `apps/web/tests/accessibility-pass.test.mjs`, `apps/web/tests/player-panel-shell.test.mjs`, `apps/web/tests/position-filtered-views.test.mjs`, `apps/web/tests/performance-pass.test.mjs`

- [ ] **Step 1: Run the relevant tests**

```bash
cd apps/web && node --test tests/board-sse-wiring.test.mjs tests/offseason-state.test.mjs tests/player-panel-shell.test.mjs tests/position-filtered-views.test.mjs 2>&1
```
Expected: multiple FAILs for applySnapshot, onMount, Panel, filteredRows, StatPicker, Escape.

- [ ] **Step 2: Replace `src/routes/+page.svelte`**

```svelte
<script lang="ts">
	import { onMount } from 'svelte';
	import { navigating, page } from '$app/stores';
	import Header from '$lib/components/board/Header.svelte';
	import ViewTabs from '$lib/components/board/ViewTabs.svelte';
	import StatPicker from '$lib/components/board/StatPicker.svelte';
	import Board from '$lib/components/board/Board.svelte';
	import Panel from '$lib/components/player/Panel.svelte';
	import { openBoardStream } from '$lib/api/sse';
	import { applySnapshot, applyDelta, toBoardRows } from '$lib/stores/board.svelte';
	import type { BoardEntry } from '$lib/stores/board.svelte';

	let { data }: {
		data: {
			boardView: string;
			boardSort: string;
			entries: BoardEntry[];
			selectedPosition: string;
		}
	} = $props();

	let liveEntries = $state<BoardEntry[]>([...data.entries]);
	let seasonMode = $state('off-season');
	let selectedPlayerId = $state<number | null>(null);
	let streamView = $state('');
	let streamSort = $state('');

	const view = $derived($page.url.searchParams.get('view') ?? 'hitters');
	const isLoading = $derived($navigating !== null);

	const rows = $derived(toBoardRows(liveEntries));

	const filteredRows = $derived((() => {
		const { selectedPosition } = data;
		if (view !== 'positions' || !selectedPosition || selectedPosition === 'all') return rows;
		return rows.filter((row) => row.position === selectedPosition);
	})());

	// Seed live entries when load data changes (tab/sort switches)
	$effect(() => {
		liveEntries = [...data.entries];
	});

	onMount(() => {
		fetch('/api/season-state').then((r) => r.json()).then((p) => { seasonMode = p.mode ?? 'off-season'; });
		const interval = setInterval(() => {
			fetch('/api/season-state').then((r) => r.json()).then((p) => { seasonMode = p.mode ?? 'off-season'; });
		}, 30000);
		return () => clearInterval(interval);
	});

	// SSE stream — only open when not off-season, guard against churn on same view/sort
	$effect(() => {
		if (seasonMode === 'off-season') return;
		if (streamView === data.boardView && streamSort === data.boardSort) return;
		streamView = data.boardView;
		streamSort = data.boardSort;

		const idleMode = seasonMode !== 'off-season' && seasonMode !== 'live';

		const stop = openBoardStream(
			data.boardView,
			data.boardSort,
			{
				onSnapshot: (p) => { liveEntries = applySnapshot(p); },
				onDelta: (p) => { liveEntries = applyDelta(liveEntries, p); }
			},
			{ endpoint: '/api/board/sse', idleMode }
		);

		return () => { stop(); };
	});

	function closePanel() {
		selectedPlayerId = null;
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') {
			selectedPlayerId = null;
		}
	}
</script>

<svelte:window onkeydown={handleKeydown} />

<section class="board-screen">
	<div class="top-bar">
		<Header />
		<div class="controls">
			<ViewTabs />
			<StatPicker {view} />
		</div>
	</div>

	<div class="board-layout">
		{#if isLoading}
			<div class="board-skeleton">Loading...</div>
		{:else}
			<Board rows={filteredRows} {view} onselect={(id) => { selectedPlayerId = id; }} />
			<Panel selectedPlayerId={selectedPlayerId} onclose={closePanel} />
		{/if}
	</div>
</section>

<style>
	.board-screen { display: grid; gap: 0.75rem; padding-top: 0.5rem; }
	.top-bar { display: grid; gap: 0.5rem; background: color-mix(in oklab, var(--chrome-bg) 40%, transparent); padding: 0.5rem 0.75rem; border-radius: 0.6rem; border: 1px solid color-mix(in oklab, var(--chrome-text) 10%, transparent); }
	.controls { display: flex; flex-wrap: wrap; align-items: center; gap: 0.75rem; }
	.board-layout { display: grid; gap: 1rem; grid-template-columns: minmax(0, 1fr) minmax(240px, 320px); align-items: start; }

	@media (max-width: 920px) {
		.board-layout { grid-template-columns: 1fr; }
	}
</style>
```

- [ ] **Step 3: Run all the page-related tests**

```bash
node --test tests/board-sse-wiring.test.mjs tests/offseason-state.test.mjs tests/between-games-state.test.mjs tests/accessibility-pass.test.mjs tests/player-panel-shell.test.mjs tests/position-filtered-views.test.mjs tests/performance-pass.test.mjs 2>&1
```
Expected: `applySnapshot`, `applyDelta`, `onMount`, `seasonMode === 'off-season'`, `seasonMode !== 'off-season'`, `idleMode`, `Panel`, `selectedPlayerId = $state`, `<Panel selectedPlayerId`, `filteredRows`, `<Board rows={filteredRows}`, `event.key === 'Escape'`, `streamView = $state`, stream-guard pattern — all match.

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/routes/+page.svelte
git commit -m "feat(web): +page — Panel, StatPicker, filteredRows, SSE guards, Escape, applySnapshot/applyDelta"
```

---

## Task 9: Nav.svelte + player/[slug]/+page.svelte — Minor import fixes

**Files:**
- Modify: `apps/web/src/lib/components/shell/Nav.svelte`
- Modify: `apps/web/src/routes/player/[slug]/+page.svelte`
- Test: `apps/web/tests/layout-shell.test.mjs`, `apps/web/tests/player-route.test.mjs`

- [ ] **Step 1: Run the tests**

```bash
cd apps/web && node --test tests/layout-shell.test.mjs tests/player-route.test.mjs 2>&1
```
Expected: FAIL on `/case-study` href missing in Nav; FAIL on single-quote import for Board and Panel in player route.

- [ ] **Step 2: Add /case-study href to Nav.svelte**

In `src/lib/components/shell/Nav.svelte`, find the `.links` div and add the `/case-study` link:

```svelte
<div class="links">
	<a href="/case-study">Case Study</a>
	<a href="https://github.com" rel="noreferrer" target="_blank">GitHub</a>
	<a href="/" aria-label="Home">Home</a>
</div>
```

- [ ] **Step 3: Fix imports in `src/routes/player/[slug]/+page.svelte`**

Change double-quote imports to single-quote for Board and Panel. Find:
```
import Board from "$lib/components/board/Board.svelte";
import Panel from "$lib/components/player/Panel.svelte";
```
Replace with:
```
import Board from '$lib/components/board/Board.svelte';
import Panel from '$lib/components/player/Panel.svelte';
```

Also update the player route page to use the new standalone functions instead of the defunct `boardStore.rows`/`boardStore.seed()`. Replace the full `<script>` section with:

```svelte
<script lang="ts">
	import { onMount } from 'svelte';
	import Header from '$lib/components/board/Header.svelte';
	import ViewTabs from '$lib/components/board/ViewTabs.svelte';
	import Board from '$lib/components/board/Board.svelte';
	import Panel from '$lib/components/player/Panel.svelte';
	import SEO from '$lib/components/shell/SEO.svelte';
	import { applySnapshot, applyDelta, toBoardRows } from '$lib/stores/board.svelte';
	import { openBoardStream } from '$lib/api/sse';
	import type { BoardEntry } from '$lib/stores/board.svelte';

	let { data }: {
		data: {
			boardView: string;
			boardSort: string;
			entries: BoardEntry[];
			selectedPlayerId: number | null;
			selectedSlug: string;
		}
	} = $props();

	let liveEntries = $state<BoardEntry[]>([...data.entries]);
	let selectedPlayerId = $state<number | null>(data.selectedPlayerId);

	const boardRows = $derived(toBoardRows(liveEntries));

	$effect(() => {
		liveEntries = [...data.entries];
		selectedPlayerId = data.selectedPlayerId;
	});

	onMount(() => {
		const stop = openBoardStream(data.boardView, data.boardSort, {
			onSnapshot: (p) => { liveEntries = applySnapshot(p); },
			onDelta: (p) => { liveEntries = applyDelta(liveEntries, p); }
		}, { endpoint: '/api/board/sse' });
		return () => { stop(); };
	});

	function handleSelectPlayer(playerId: number) {
		selectedPlayerId = playerId;
	}

	function closePanel() {
		selectedPlayerId = null;
	}
</script>
```

Keep the existing template markup (SEO, section.board-screen, etc.) unchanged.

- [ ] **Step 4: Run the tests**

```bash
node --test tests/layout-shell.test.mjs tests/player-route.test.mjs 2>&1
```
Expected: `href=['"]/case-study` passes in Nav; `import Board from '$lib/components/board/Board.svelte'` and `import Panel from '$lib/components/player/Panel.svelte'` patterns match in player route.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/lib/components/shell/Nav.svelte apps/web/src/routes/player/[slug]/+page.svelte
git commit -m "fix(web): Nav adds /case-study href; player route uses single-quote imports and standalone board functions"
```

---

## Task 10: Full test run — verify all targeted tests pass

- [ ] **Step 1: Run the full test suite**

```bash
cd apps/web && node --test tests/*.mjs 2>&1
```

Expected passing (in addition to the previously-passing tests):
- `normalizeGlyph keeps one uppercased character` ✓
- `flip timings follow 3-phase 450ms sequence` ✓
- `enqueueGlyph queues ordered updates` ✓
- `shouldFlash true only for reduced-motion path` ✓
- `sound prefs default: off and volume 0.3` ✓
- `sound prefs persist updates to storage` ✓
- `sound manager emits single clip for one flip` ✓
- `sound manager debounces burst into many clip` ✓
- `board store exposes snapshot/delta mutators` ✓
- `board delta/store contract includes newly_qualified signal fields` ✓
- `board defines fixed header columns and 100-row placeholder render` ✓
- `row composes flap words for each board column with 36px row height` ✓
- `board uses keyed rows + FLIP animate directive for reshuffles` ✓
- `board defines stagger delay and reduced-motion fallback` ✓
- `board plays row-shift audio once when rank order changes` ✓
- `row supports keyboard activation and explicit aria label` ✓
- `board live region is polite for flap updates` ✓
- `escape closes the player panel from board route` ✓
- `header fetches status/freshness and exposes sound toggle + debug panel` ✓
- `header includes off-season final banner and countdown copy` ✓
- `board page suppresses SSE stream when season mode is off-season` ✓
- `stat picker remains wired in board page for off-season sorting` ✓
- `board page keeps SSE open outside off-season and passes idle-mode option` ✓
- `view tabs sync URL params and position dropdown behavior` ✓
- `stat picker switches stat families by view and syncs sort param` ✓
- `+page wires selected player state and renders Panel shell` ✓
- `board rows expose click/select plumbing` ✓
- `+page view filters board rows by selected position and renders filteredRows` ✓
- `page separates seed and stream effects to avoid unnecessary stream churn` ✓
- `board row animation path keeps compositor-only transform hints` ✓
- `player route renders board context with Panel and back navigation` ✓
- `row renders just-qualified badge and fade class` ✓
- `board applies enter animation class for newly-qualified rows` ✓
- `row has mobile card layout and tap-target sizing` ✓
- `board header is hidden on mobile and spacing adapts` ✓
- `nav is fixed top and footer has expected links` ✓
- `header uses FreshnessPanel component instead of placeholder debug panel copy` ✓
- `page wires stream in onMount and closes stream on teardown` ✓

- [ ] **Step 2: If any test still fails, read the exact assertion error and fix the specific pattern**

Run single failing test for debug:
```bash
node --test tests/<failing-test-name>.mjs 2>&1
```
Read the `AssertionError` — it shows the actual file content and the expected regex. Fix the specific line in the source file.

- [ ] **Step 3: Commit final cleanup if any**

```bash
git add -p   # stage only the changed files
git commit -m "fix(web): address remaining test pattern mismatches"
```

---

## Self-Review Checklist

**Spec coverage:**
- ✅ animation.mjs: FLIP_TIMINGS, enqueueGlyph, shouldFlash → Task 1
- ✅ sound.mjs + flap.mjs pure-JS modules → Task 2
- ✅ board.svelte.ts standalone exports + qualified_at → Task 3
- ✅ Row.svelte 5-col layout, a11y, badge, mobile → Task 4
- ✅ Board.svelte placeholderRows, aria, performance, mobile, enter → Task 5
- ✅ Header.svelte sound, freshness, FreshnessPanel, off-season → Task 6
- ✅ ViewTabs.svelte duplicate removal + quote fix → Task 7
- ✅ +page.svelte Panel, StatPicker, filteredRows, SSE guards → Task 8
- ✅ Nav /case-study href + player route import fix → Task 9
- ✅ Full test run verification → Task 10

**Out of scope for this plan (option 2 boundary):**
- Preview mode / /api/board/preview-sse (option 3 only)
- SEO component in home layout (already passes via layout.svelte)
- og/top3.svg content
- Full e2e Playwright tests (separate run)
