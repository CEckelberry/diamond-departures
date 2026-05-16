# E-Ink Display Mode Implementation Design

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a three-state e-ink display mode (Off / Aesthetic / Faithful) that transforms the board into a high-contrast paper-like display, with auto-detection for real e-ink hardware.

**Architecture:** CSS custom-property theme swap via a body class, driven by a small Svelte store that reads/writes `localStorage`. No component logic changes beyond the header toggle and Cell animation speed.

**Tech Stack:** SvelteKit 5 (Runes), CSS custom properties, `localStorage`, `window.matchMedia`

---

## Theme System

The existing dark theme uses CSS custom properties (`--cell-bg`, `--cell-text`, `--board-bg`, `--cell-edge`, `--chrome-bg`, `--chrome-text`, `--mlb-blue`, `--mlb-red`). These are currently set on `:root` in the global stylesheet.

E-ink modes add two body classes — `.eink-aesthetic` and `.eink-faithful` — that override those properties. Both modes share the same palette; Faithful additionally disables all animation.

**Shared e-ink palette overrides:**
```css
body.eink-aesthetic,
body.eink-faithful {
  --cell-bg: #f5f0e8;
  --cell-text: #0a0a0a;
  --cell-edge: #0a0a0a;
  --board-bg: #f5f0e8;
  --chrome-bg: #ede9e0;
  --chrome-text: #0a0a0a;
  --mlb-blue: #0a0a0a;
  --mlb-red: #0a0a0a;
}
```

No gradients, no color accents. The board-rail (blue/red stripe) becomes a single black line. The yellow sort highlight becomes black.

**Faithful-only animation kill:**
```css
body.eink-faithful * {
  animation-duration: 0ms !important;
  transition-duration: 0ms !important;
}
```

**Aesthetic-only animation slowdown:** Passed as a prop override to `Cell.svelte` — `flipDuration` becomes `350ms` and stagger is increased so each cell flip is individually visible rather than all firing at once.

---

## Theme Store

**File:** `apps/web/src/lib/stores/eink.ts`

```typescript
export type EinkMode = 'off' | 'aesthetic' | 'faithful';

const STORAGE_KEY = 'eink-mode';

function createEinkStore() {
  let mode = $state<EinkMode>('off');

  function init() {
    const saved = localStorage.getItem(STORAGE_KEY) as EinkMode | null;
    if (saved === 'aesthetic' || saved === 'faithful') {
      mode = saved;
    }
    applyClass(mode);
  }

  function set(next: EinkMode) {
    mode = next;
    localStorage.setItem(STORAGE_KEY, next);
    applyClass(next);
  }

  function applyClass(m: EinkMode) {
    document.body.classList.remove('eink-aesthetic', 'eink-faithful');
    if (m === 'aesthetic') document.body.classList.add('eink-aesthetic');
    if (m === 'faithful') document.body.classList.add('eink-faithful');
  }

  return { get mode() { return mode; }, init, set };
}

export const einkStore = createEinkStore();
```

**Auto-detection** runs inside `init()`, before checking `localStorage`: if `window.matchMedia('(prefers-reduced-motion: reduce)').matches` AND `window.screen.colorDepth <= 8`, and no explicit `localStorage` value exists, default to `'faithful'`.

`init()` is called once in the root `+layout.svelte` `onMount`.

---

## Toggle Component

**File:** `apps/web/src/lib/components/board/EinkToggle.svelte`

Placed in `Header.svelte` next to the existing sound button. Cycles Off → Aesthetic → Faithful on each click.

- **Off:** monitor icon, no label
- **Aesthetic:** monitor icon + "PAPER" label
- **Faithful:** monitor icon + "E-INK" label (or "AUTO" if auto-detected)

The button uses the same `.icon-btn` class as the sound toggle for visual consistency.

---

## Cell Animation Adjustment

**File:** `apps/web/src/lib/components/flap/Cell.svelte`

When `eink-aesthetic` is active, `flipDuration` is overridden to `350ms`. The store value is read via a derived binding passed down from the Word → Cell chain, or more simply, Cell reads `document.body.classList.contains('eink-aesthetic')` once at mount.

Faithful mode skips this — the CSS `animation-duration: 0ms !important` already handles it.

---

## Global CSS Changes

**File:** `apps/web/src/app.css` (or equivalent global stylesheet)

- Add `.eink-aesthetic` / `.eink-faithful` palette overrides (as above)
- Add `body.eink-faithful * { animation-duration: 0ms !important; transition-duration: 0ms !important; }`
- Override yellow sort highlight: `body.eink-aesthetic .stat-head, body.eink-faithful .stat-head { color: #0a0a0a; }`
- Override board rail: `body.eink-aesthetic .board-rail, body.eink-faithful .board-rail { background: #0a0a0a; }`

---

## Persistence & Profile Integration

- `localStorage` key: `eink-mode`, values: `"off"` | `"aesthetic"` | `"faithful"`
- When user profiles are added (future auth spec), this preference becomes a profile field. On login, the server-stored preference overwrites the `localStorage` value.
- Auto-detected Faithful mode does **not** write to `localStorage` — it stays ephemeral so the user's stored preference (if they later set one) takes precedence.

---

## What This Does NOT Include

- Server-side rendering of the theme (avoids flash-of-wrong-theme by applying the class in `onMount`)
- Profile settings UI for this toggle (built during auth spec)
- Any changes to the board data layer or API

---

## Files Touched

| File | Change |
|------|--------|
| `apps/web/src/app.css` | Add e-ink CSS class overrides |
| `apps/web/src/lib/stores/eink.ts` | New — theme store with auto-detect |
| `apps/web/src/lib/components/board/EinkToggle.svelte` | New — three-state toggle button |
| `apps/web/src/lib/components/board/Header.svelte` | Add `EinkToggle`, call `einkStore.init()` |
| `apps/web/src/lib/components/flap/Cell.svelte` | Slow flip duration in aesthetic mode |
| `apps/web/src/routes/+layout.svelte` | Call `einkStore.init()` on mount |
