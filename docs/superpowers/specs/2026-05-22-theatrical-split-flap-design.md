# Theatrical Split-Flap Animation — Design Spec

**Date:** 2026-05-22  
**Status:** Approved

## Summary

Upgrade the split-flap cell animation from a fast 120ms mechanical flip to a slower, more deliberate "theatrical" style (190ms flip, 75ms per-column stagger, 3 intermediate characters). Apply the theatrical style to SSE live stat updates only. Sort and view/style switches keep their existing snap-then-row-glide behavior.

## Motivation

The current animation fires all cells simultaneously on any data change, creating visual chaos at scale. After diagnosing and fixing the root race condition (URL params vs. async data arrival), the board is stable. The next step is making individual stat updates feel premium — the way a real Solari departure board looks when a flight gate changes.

The theatrical style was validated in a single-row interactive demo (`animation-approaches.html`) and selected by the user over two faster alternatives.

## Behavior Matrix

| Trigger | Cell behavior | Row behavior |
|---|---|---|
| View switch (hitters↔pitchers/defense/positions) | **Snap** — `anim.snap` guard, unchanged | Instant |
| Style switch (Sabermetric / Traditional) | **Snap** — `anim.snap` guard, unchanged | Instant |
| Sort column click | **Snap** — `anim.snap` guard, unchanged | **Glide** — existing `animate:flip` (delay: rowIdx × 30ms, 300ms cubicOut) |
| **SSE live stat update** | **Theatrical flip** — 190ms, colIndex × 75ms stagger, 3 intermediates | Glide if rank changes (same `animate:flip`) |
| Initial page-load intro | Fast cascade — existing staggerIndex × 2ms, bumped to 190ms flip | — |

## Animation Parameters (Theatrical)

| Parameter | Value |
|---|---|
| Flip duration | 190ms |
| Easing | `cubic-bezier(0.4, 0, 1, 1)` (existing gravity curve) |
| Column stagger | 75ms × `colIndex` |
| Intermediates (far jump, >3 glyphs away) | 3 evenly-spaced glyphs + target |
| Intermediates (close jump, ≤3 glyphs) | Step directly (1–3 flips, unchanged) |

## Architecture

### Files changed

**`apps/web/src/lib/components/flap/Cell.svelte`** — two additions:

1. New `colIndex = 0` prop (the cell's absolute column position within its row, 0-based).
2. Base `flipDuration` bumped from 120ms → 190ms (applies to both intro and live updates; eink overrides unchanged).
3. In the live-value `$effect`: wrap the queue-building logic in `setTimeout(colIndex * 75, fn)`. Re-check `anim.snap` inside the callback to handle the race where a sort click lands during a pending timer.
4. "Far" jump intermediates changed from 2 → 3.

**`apps/web/src/lib/components/flap/Word.svelte`** — one addition:

Pass `colIndex={baseColIndex + index}` to each `<Cell>`. The existing `staggerIndex` prop (used for the intro cascade) is kept unchanged.

### Files NOT changed

| File | Reason |
|---|---|
| `Board.svelte` | `animate:flip` row glide already correct; no changes needed |
| `Row.svelte` | `baseColIndex` values already correct for all word groups |
| `+page.svelte` | `anim.snap` guard already fires before data arrives |
| `board.svelte.ts` | `AnimControl` shape unchanged |
| `+page.ts` | Load function unchanged |

## Column Index Reference

`colIndex = baseColIndex + index` per the existing `Row.svelte` constants:

| Group | `baseColIndex` | Cells | colIndex range |
|---|---|---|---|
| Rank | 0 | 3 | 0–2 |
| Player name | 3 | 1–18 | 3–20 |
| Team | 21 | 3 | 21–23 |
| Position | 24 | 2 | 24–25 |
| Stat col 0–6 | 26 + colIdx × 5 | 3–5 | 26–60 |

With 75ms stagger, the last stat cell in a row begins flipping at ~60 × 75ms = 4500ms after the update. In practice SSE deltas change 1–5 rows with 1–3 stat cells each, so visible motion is concentrated in a small area and completes in under a second.

## Race Condition Guard

The live-update `$effect` currently checks `anim.snap` synchronously before queuing. Adding `setTimeout` introduces a window where the user could click a sort column after a timer is started but before it fires. The fix: check `anim.snap` a second time inside the callback and bail if true.

```
$effect fires → anim.snap? → false → setTimeout(delay)
                                         ↓ (delay ms later)
                                      anim.snap? → false → queue flip
                                                 → true  → discard (snap guard)
```

## Testing

Existing tests in `board-sse-wiring.test.mjs` and `just-qualified-animation.test.mjs` remain valid; no new test contracts are introduced by this change. Manual verification: open the board during a live game (or SSE idle-mode simulation), change a stat value via the dev API, and confirm the theatrical cascade fires column-by-column.
