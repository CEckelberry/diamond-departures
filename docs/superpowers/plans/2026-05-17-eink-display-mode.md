# E-Ink Display Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a three-state e-ink display mode (Off / Aesthetic / Faithful) with auto-detection, a header toggle, and reactive Cell animation speed.

**Architecture:** A Svelte 4 writable store (`eink.ts`) manages mode state, persists to `localStorage`, and applies CSS body classes. The global stylesheet defines palette + animation overrides under those classes. `Cell.svelte` reads the store to adjust its JavaScript `flipDuration` timer. A new `EinkToggle.svelte` button cycles through modes and lives in `Header.svelte`.

**Tech Stack:** SvelteKit 5 (Runes + Svelte 4 stores), CSS custom properties, `localStorage`, `window.matchMedia`

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `apps/web/src/lib/stores/eink.ts` | Create | Mode state, localStorage, auto-detect, body class application |
| `apps/web/src/app.css` | Modify | `.eink-aesthetic` / `.eink-faithful` palette + animation overrides |
| `apps/web/src/lib/components/board/EinkToggle.svelte` | Create | Three-state toggle button, cycles Off→Aesthetic→Faithful |
| `apps/web/src/lib/components/board/Header.svelte` | Modify | Import + render EinkToggle |
| `apps/web/src/routes/+layout.svelte` | Modify | Call `einkStore.init()` on mount |
| `apps/web/src/lib/components/flap/Cell.svelte` | Modify | Reactive `flipDuration` from eink store |
| `apps/web/tests/eink-mode.test.mjs` | Create | Static source-pattern tests for all of the above |

---

### Task 1: E-Ink Store

**Files:**
- Create: `apps/web/src/lib/stores/eink.ts`
- Test: `apps/web/tests/eink-mode.test.mjs`

- [ ] **Step 1: Write the failing test**

Create `apps/web/tests/eink-mode.test.mjs`:

```javascript
import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const storePath = new URL("../src/lib/stores/eink.ts", import.meta.url);
const cssPath = new URL("../src/app.css", import.meta.url);
const togglePath = new URL("../src/lib/components/board/EinkToggle.svelte", import.meta.url);
const headerPath = new URL("../src/lib/components/board/Header.svelte", import.meta.url);
const layoutPath = new URL("../src/routes/+layout.svelte", import.meta.url);
const cellPath = new URL("../src/lib/components/flap/Cell.svelte", import.meta.url);

async function load(path) {
  return readFile(path, "utf8");
}

test("eink store exports einkStore with init and cycle", async () => {
  const src = await load(storePath);
  assert.match(src, /export\s+const\s+einkStore/);
  assert.match(src, /init\s*\(/);
  assert.match(src, /cycle\s*\(/);
});

test("eink store exports STORAGE_KEY", async () => {
  const src = await load(storePath);
  assert.match(src, /STORAGE_KEY/);
  assert.match(src, /eink-mode/);
});

test("eink store auto-detect checks prefers-reduced-motion and colorDepth", async () => {
  const src = await load(storePath);
  assert.match(src, /prefers-reduced-motion/);
  assert.match(src, /colorDepth/);
});

test("eink store applies body classes", async () => {
  const src = await load(storePath);
  assert.match(src, /eink-aesthetic/);
  assert.match(src, /eink-faithful/);
  assert.match(src, /classList/);
});

test("app.css has eink-aesthetic palette overrides", async () => {
  const src = await load(cssPath);
  assert.match(src, /\.eink-aesthetic/);
  assert.match(src, /#f5f0e8/);
});

test("app.css has eink-faithful animation kill", async () => {
  const src = await load(cssPath);
  assert.match(src, /\.eink-faithful/);
  assert.match(src, /animation-duration:\s*0ms/);
});

test("EinkToggle imports einkStore and cycles modes", async () => {
  const src = await load(togglePath);
  assert.match(src, /einkStore/);
  assert.match(src, /cycle/);
});

test("Header imports EinkToggle", async () => {
  const src = await load(headerPath);
  assert.match(src, /EinkToggle/);
});

test("layout calls einkStore.init on mount", async () => {
  const src = await load(layoutPath);
  assert.match(src, /einkStore/);
  assert.match(src, /init/);
  assert.match(src, /onMount/);
});

test("Cell imports einkStore and uses it for flipDuration", async () => {
  const src = await load(cellPath);
  assert.match(src, /einkStore/);
  assert.match(src, /aesthetic/);
  assert.match(src, /faithful/);
});
```

- [ ] **Step 2: Run tests to confirm they all fail**

```bash
cd apps/web && node --test tests/eink-mode.test.mjs
```

Expected: all 10 tests FAIL (files don't exist yet).

- [ ] **Step 3: Create the store**

Create `apps/web/src/lib/stores/eink.ts`:

```typescript
import { browser } from '$app/environment';
import { writable } from 'svelte/store';

export type EinkMode = 'off' | 'aesthetic' | 'faithful';

export const STORAGE_KEY = 'eink-mode';

function detectEink(): boolean {
  if (!browser) return false;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const lowColorDepth = window.screen.colorDepth <= 8;
  return reducedMotion && lowColorDepth;
}

function applyClass(mode: EinkMode) {
  if (!browser) return;
  document.body.classList.remove('eink-aesthetic', 'eink-faithful');
  if (mode === 'aesthetic') document.body.classList.add('eink-aesthetic');
  if (mode === 'faithful') document.body.classList.add('eink-faithful');
}

function createEinkStore() {
  const { subscribe, set, update } = writable<EinkMode>('off');

  function init() {
    if (!browser) return;
    const saved = localStorage.getItem(STORAGE_KEY) as EinkMode | null;
    if (saved === 'aesthetic' || saved === 'faithful') {
      set(saved);
      applyClass(saved);
    } else if (detectEink()) {
      // auto-detected: don't persist so user's explicit choice always wins
      set('faithful');
      applyClass('faithful');
    }
  }

  function cycle() {
    update(current => {
      const next: EinkMode =
        current === 'off' ? 'aesthetic' :
        current === 'aesthetic' ? 'faithful' : 'off';
      if (browser) {
        localStorage.setItem(STORAGE_KEY, next);
        applyClass(next);
      }
      return next;
    });
  }

  return { subscribe, init, cycle };
}

export const einkStore = createEinkStore();
```

- [ ] **Step 4: Run the store tests to confirm they pass**

```bash
cd apps/web && node --test tests/eink-mode.test.mjs 2>&1 | grep -E "eink store|PASS|FAIL"
```

Expected: the 4 eink-store tests pass. CSS/component tests still fail — that's expected.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/lib/stores/eink.ts apps/web/tests/eink-mode.test.mjs
git commit -m "feat(web): add e-ink mode store with localStorage persistence and auto-detect"
```

---

### Task 2: Global CSS Overrides

**Files:**
- Modify: `apps/web/src/app.css`

- [ ] **Step 1: Add e-ink theme classes to `app.css`**

Append to the end of `apps/web/src/app.css`:

```css
/* ── E-ink Display Modes ─────────────────────────────────────────── */

body.eink-aesthetic,
body.eink-faithful {
  --board-bg: #f5f0e8;
  --cell-bg: #f5f0e8;
  --cell-edge: rgba(0, 0, 0, 0.6);
  --cell-text: #0a0a0a;
  --cell-text-dim: #3a3a3a;
  --rank-text: rgba(0, 0, 0, 0.5);
  --mlb-blue: #0a0a0a;
  --mlb-red: #0a0a0a;
  --chrome-bg: #ede9e0;
  --chrome-text: #0a0a0a;
  --accent-primary: #0a0a0a;
}

/* Override yellow sort highlight to black in e-ink modes */
body.eink-aesthetic .stat-head,
body.eink-faithful .stat-head {
  color: #0a0a0a;
}

body.eink-aesthetic .stat-active,
body.eink-faithful .stat-active {
  color: #0a0a0a !important;
}

/* Remove radial gradient from shell background */
body.eink-aesthetic .shell-main,
body.eink-faithful .shell-main {
  background: none;
}

/* Faithful mode: kill all animation and transition */
body.eink-faithful * {
  animation-duration: 0ms !important;
  transition-duration: 0ms !important;
}
```

- [ ] **Step 2: Run the CSS tests**

```bash
cd apps/web && node --test tests/eink-mode.test.mjs 2>&1 | grep -E "app.css|PASS|FAIL"
```

Expected: the 2 CSS tests now pass.

- [ ] **Step 3: Commit**

```bash
git add apps/web/src/app.css
git commit -m "feat(web): add e-ink CSS theme classes (aesthetic + faithful)"
```

---

### Task 3: EinkToggle Component

**Files:**
- Create: `apps/web/src/lib/components/board/EinkToggle.svelte`

- [ ] **Step 1: Create the toggle component**

Create `apps/web/src/lib/components/board/EinkToggle.svelte`:

```svelte
<script lang="ts">
  import { einkStore } from '$lib/stores/eink';
  import type { EinkMode } from '$lib/stores/eink';

  const LABELS: Record<EinkMode, string> = {
    off: '🖥',
    aesthetic: '📄',
    faithful: '🖫',
  };

  const ARIA: Record<EinkMode, string> = {
    off: 'Enable e-ink aesthetic mode',
    aesthetic: 'Enable faithful e-ink mode',
    faithful: 'Disable e-ink mode',
  };
</script>

<button
  class="icon-btn"
  class:eink-active={$einkStore !== 'off'}
  type="button"
  aria-label={ARIA[$einkStore]}
  onclick={() => einkStore.cycle()}
>
  {LABELS[$einkStore]}
  {#if $einkStore !== 'off'}
    <span class="eink-label">{$einkStore === 'aesthetic' ? 'PAPER' : 'E-INK'}</span>
  {/if}
</button>

<style>
  .eink-active {
    border-color: color-mix(in oklab, var(--chrome-text) 50%, transparent);
  }

  .eink-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-left: 0.2rem;
  }
</style>
```

- [ ] **Step 2: Run the toggle test**

```bash
cd apps/web && node --test tests/eink-mode.test.mjs 2>&1 | grep -E "EinkToggle|PASS|FAIL"
```

Expected: the EinkToggle test passes.

- [ ] **Step 3: Commit**

```bash
git add apps/web/src/lib/components/board/EinkToggle.svelte
git commit -m "feat(web): add EinkToggle component cycling off/aesthetic/faithful"
```

---

### Task 4: Wire Toggle into Header and Init in Layout

**Files:**
- Modify: `apps/web/src/lib/components/board/Header.svelte`
- Modify: `apps/web/src/routes/+layout.svelte`

The current `Header.svelte` has a `<div class="status-row">` containing two `.icon-btn` buttons (sound toggle and freshness toggle). Add `EinkToggle` between them. The current `+layout.svelte` has no `<script>` tag — add one.

- [ ] **Step 1: Update Header.svelte**

In `apps/web/src/lib/components/board/Header.svelte`, add the import at the top of the `<script>` block (after the existing imports):

```svelte
import EinkToggle from '$lib/components/board/EinkToggle.svelte';
```

Then in the template, add `<EinkToggle />` between the sound button and the freshness button:

```svelte
<div class="status-row">
  {#if seasonState.mode !== 'off-season'}
    <span class={`mode-pill ${modeClass}`}>{seasonState.mode}</span>
  {/if}

  {#if seasonState.mode === 'off-season'}
    <span class="status-pill off-season-banner">
      {seasonState.currentSeason ?? 2026} regular season · final — next season starts soon
    </span>
  {:else if seasonState.mode === 'between' || seasonState.mode === 'off-game'}
    <span class="status-pill idle-banner">{idleBannerCopy}</span>
  {:else}
    <span class="status-pill">{seasonState.gamesInProgress} games live</span>
  {/if}

  <button class="icon-btn" type="button" aria-label="Toggle sound" onclick={toggleSound}>
    {$soundEnabled ? '🔊' : '🔇'}
  </button>

  <EinkToggle />

  <button class="icon-btn freshness-btn" type="button" aria-label="Show freshness debug panel" onclick={toggleFreshnessDebug}>
    ⏱
  </button>
</div>
```

- [ ] **Step 2: Update +layout.svelte**

Replace the entire content of `apps/web/src/routes/+layout.svelte`:

```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import '../app.css';
  import favicon from '$lib/assets/favicon.svg';
  import Nav from '$lib/components/shell/Nav.svelte';
  import Footer from '$lib/components/shell/Footer.svelte';
  import SEO from '$lib/components/shell/SEO.svelte';
  import { einkStore } from '$lib/stores/eink';

  let { children } = $props();

  onMount(() => {
    einkStore.init();
  });
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
<SEO
  title="Diamond Departures"
  description="Live fantasy baseball movement board for departures, trends, and qualification shifts."
  path="/"
/>

<div class="app-shell">
  <Nav />
  <main class="shell-main">{@render children()}</main>
  <Footer />
</div>
```

- [ ] **Step 3: Run Header + Layout tests**

```bash
cd apps/web && node --test tests/eink-mode.test.mjs 2>&1 | grep -E "Header|layout|PASS|FAIL"
```

Expected: both tests pass.

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/lib/components/board/Header.svelte apps/web/src/routes/+layout.svelte
git commit -m "feat(web): wire EinkToggle into header, init eink store in layout"
```

---

### Task 5: Cell Animation Reactivity

**Files:**
- Modify: `apps/web/src/lib/components/flap/Cell.svelte`

`Cell.svelte` currently has `const flipDuration = 42 * timingSkew` as a fixed constant. We need it to react to the e-ink store so aesthetic mode slows flips to 350ms and faithful mode drops them to 1ms (effectively instant, complementing the CSS `animation-duration: 0ms`).

The current `Cell.svelte` top of script:
```typescript
const timingSkew = 0.85 + (Math.random() * 0.3);
const flipDuration = 42 * timingSkew;
```

- [ ] **Step 1: Update Cell.svelte**

In `apps/web/src/lib/components/flap/Cell.svelte`, replace the top of the `<script>` block to add the store import and make `flipDuration` reactive. The full updated script section (replace everything from line 1 through the existing `const flipDuration` line):

```svelte
<script lang="ts">
  import { onMount, untrack } from "svelte";
  import { normalizeGlyph, GLYPHS } from "./animation.mjs";
  import { noteFlapFlip } from "$lib/audio/flap";
  import { einkStore } from "$lib/stores/eink";

  let { value, width = 28, height = 36, onFlip = () => {}, staggerIndex = 0 } = $props();

  const targetGlyph = $derived(normalizeGlyph(value));
  let currentGlyph = $state(" ");
  let nextGlyph = $state(" ");
  let isFlipping = $state(false);

  const timingSkew = 0.85 + (Math.random() * 0.3);
  const flipDuration = $derived(
    ($einkStore === 'aesthetic' ? 350 :
     $einkStore === 'faithful' ? 1 : 42) * timingSkew
  );
  const halfHeight = Math.floor(height / 2);
```

The rest of `Cell.svelte` (from `// Single queue + timer` onward) stays exactly as-is. Only the top of the script section changes.

Also update the `style` attribute on the `.cell` div to use the reactive `flipDuration`. Find this line in the template:

```svelte
style="--cell-width:{width}px;--cell-height:{height}px;--half-height:{halfHeight}px;--flip-duration:{flipDuration}ms;"
```

It already references `flipDuration` — no change needed there since it's now a `$derived` and will update reactively.

- [ ] **Step 2: Run the Cell test**

```bash
cd apps/web && node --test tests/eink-mode.test.mjs 2>&1 | grep -E "Cell|PASS|FAIL"
```

Expected: Cell test passes.

- [ ] **Step 3: Run all eink tests**

```bash
cd apps/web && node --test tests/eink-mode.test.mjs
```

Expected: all 10 tests pass.

- [ ] **Step 4: Build check**

```bash
cd apps/web && npx tsc --noEmit 2>&1 | head -20
```

Expected: no TypeScript errors.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/lib/components/flap/Cell.svelte
git commit -m "feat(web): Cell flip duration reacts to e-ink mode (350ms aesthetic, 1ms faithful)"
```

---

### Task 6: Visual Verification

- [ ] **Step 1: Rebuild Docker container**

```bash
cd /path/to/diamond-departures && docker compose up --build web -d
```

Wait ~10 seconds for the container to start, then verify `curl -s http://localhost:5173 | head -3` returns HTML.

- [ ] **Step 2: Screenshot default (Off) mode**

```bash
cd apps/web && npx playwright screenshot --browser=chromium --wait-for-timeout=6000 "http://localhost:5173" /tmp/eink-off.png
```

Expected: dark theme, normal board.

- [ ] **Step 3: Screenshot aesthetic mode via URL + localStorage manipulation**

Use Playwright to set localStorage and reload:

```bash
npx playwright screenshot --browser=chromium --wait-for-timeout=6000 \
  "http://localhost:5173" \
  --storage-state='{"cookies":[],"origins":[{"origin":"http://localhost:5173","localStorage":[{"name":"eink-mode","value":"aesthetic"}]}]}' \
  /tmp/eink-aesthetic.png
```

Expected: light cream background, black text, no color accents.

- [ ] **Step 4: Screenshot faithful mode**

```bash
npx playwright screenshot --browser=chromium --wait-for-timeout=6000 \
  "http://localhost:5173" \
  --storage-state='{"cookies":[],"origins":[{"origin":"http://localhost:5173","localStorage":[{"name":"eink-mode","value":"faithful"}]}]}' \
  /tmp/eink-faithful.png
```

Expected: same palette as aesthetic, no animation movement visible.

- [ ] **Step 5: Commit**

No code changes — just confirm visuals look correct before closing the feature.

```bash
git add -p  # stage any incidental fixes from verification
git commit -m "feat(web): e-ink display mode complete (off/aesthetic/faithful + auto-detect)"
```
