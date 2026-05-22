# Theatrical Split-Flap Animation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade live SSE stat updates to a theatrical split-flap style — 190ms flip, 75ms left-to-right column stagger, 3 intermediate characters — while keeping sort/view/style switches as instant snaps with row-glide reordering.

**Architecture:** Two files change: `Cell.svelte` gains a `colIndex` prop and wraps its live-update flip queue in a `setTimeout(colIndex * 75)` with a double `anim.snap` guard; `Word.svelte` passes `colIndex={baseColIndex + index}` to each Cell. Everything else (snap guard, animate:flip row glide, SSE wiring) is unchanged.

**Tech Stack:** Svelte 5, CSS 3D transforms, Node.js `node:test` for source-level contract tests.

---

## File Map

| Action | Path |
|---|---|
| **Create** | `apps/web/tests/theatrical-animation.test.mjs` |
| **Modify** | `apps/web/src/lib/components/flap/Cell.svelte` |
| **Modify** | `apps/web/src/lib/components/flap/Word.svelte` |

---

### Task 1: Write Failing Tests

**Files:**
- Create: `apps/web/tests/theatrical-animation.test.mjs`

- [ ] **Step 1.1: Create the test file**

```js
import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const cellPath = new URL("../src/lib/components/flap/Cell.svelte", import.meta.url);
const wordPath = new URL("../src/lib/components/flap/Word.svelte", import.meta.url);

async function load(p) { return readFile(p, "utf8"); }

test("Cell accepts colIndex prop with default 0", async () => {
    const src = await load(cellPath);
    assert.match(src, /colIndex\s*=\s*0/);
});

test("Cell uses 190ms as base theatrical flip duration", async () => {
    const src = await load(cellPath);
    assert.match(src, /:\s*190\s*\)/);
});

test("Cell stagger delay uses colIndex * 75 for live updates", async () => {
    const src = await load(cellPath);
    assert.match(src, /colIndex\s*\*\s*75/);
});

test("Cell double-checks anim.snap inside the stagger timeout", async () => {
    const src = await load(cellPath);
    const occurrences = [...src.matchAll(/anim\.snap/g)];
    assert.ok(occurrences.length >= 2, `expected >= 2 anim.snap checks, got ${occurrences.length}`);
});

test("Cell uses 3 evenly-spaced intermediates for far-jump live updates", async () => {
    const src = await load(cellPath);
    // Match '* 0.25', '* 0.5', '* 0.75' — the three intermediate spacing multipliers
    assert.match(src, /\* 0\.25/);
    assert.match(src, /\* 0\.5\b/);
    assert.match(src, /\* 0\.75/);
});

test("Word passes colIndex to Cell", async () => {
    const src = await load(wordPath);
    assert.match(src, /colIndex=\{baseColIndex\s*\+\s*index\}/);
});
```

- [ ] **Step 1.2: Run and verify all 6 tests fail**

```bash
cd apps/web && node --test tests/theatrical-animation.test.mjs
```

Expected: 6 failures. If any pass already, check the test logic — the assertions may be too loose.

- [ ] **Step 1.3: Commit the failing tests**

```bash
git add apps/web/tests/theatrical-animation.test.mjs
git commit -m "test: add failing tests for theatrical split-flap animation contracts"
```

---

### Task 2: Add `colIndex` Prop and Bump Flip Duration in Cell.svelte

**Files:**
- Modify: `apps/web/src/lib/components/flap/Cell.svelte:8` (props line)
- Modify: `apps/web/src/lib/components/flap/Cell.svelte:16-19` (flipDuration derived)

- [ ] **Step 2.1: Add `colIndex` to props and bump flipDuration**

In `apps/web/src/lib/components/flap/Cell.svelte`, make two edits:

**Edit 1** — props line (line 8). Change:
```js
let { value, width = 28, height = 36, onFlip = () => {}, staggerIndex = 0 } = $props();
```
To:
```js
let { value, width = 28, height = 36, onFlip = () => {}, staggerIndex = 0, colIndex = 0 } = $props();
```

**Edit 2** — flipDuration derived (lines 16-19). Change:
```js
const flipDuration = $derived(
    ($einkStore === 'aesthetic' ? 350 :
     $einkStore === 'faithful' ? 1 : 120) * timingSkew
);
```
To:
```js
const flipDuration = $derived(
    ($einkStore === 'aesthetic' ? 350 :
     $einkStore === 'faithful' ? 1 : 190) * timingSkew
);
```

- [ ] **Step 2.2: Run tests — expect 2 to pass, 4 to still fail**

```bash
cd apps/web && node --test tests/theatrical-animation.test.mjs
```

Expected: `colIndex prop` and `190ms` tests pass; the other 4 still fail.

---

### Task 3: Theatrical Stagger and 3 Intermediates in Live `$effect`

**Files:**
- Modify: `apps/web/src/lib/components/flap/Cell.svelte:79-112` (the live-value `$effect`)

- [ ] **Step 3.1: Replace the post-snap-check body with staggered theatrical queue logic**

The `$effect` currently reads (lines 76-113 of Cell.svelte):

```js
// Handle live value changes after initial mount.
let mounted = false;
$effect(() => {
    const target = targetGlyph;
    if (!mounted) { mounted = true; return; }
    untrack(() => {
        // Navigation swap: skip animation, snap directly to avoid 2600-cell chaos
        if (anim.snap) {
            queue.length = 0;
            if (flipTimer) { clearTimeout(flipTimer); flipTimer = null; }
            currentGlyph = target;
            nextGlyph = target;
            isFlipping = false;
            return;
        }
        const tail = queue.length > 0 ? queue[queue.length - 1] : currentGlyph;
        const startIndex = Math.max(0, GLYPHS.indexOf(tail));
        const targetIndex = Math.max(0, GLYPHS.indexOf(target));
        if (startIndex === targetIndex) return;
        const n = GLYPHS.length;
        const fwdDist = (targetIndex - startIndex + n) % n;
        if (fwdDist <= 3) {
            // Close: step directly (1–3 flips)
            let i = (startIndex + 1) % n;
            while (true) {
                queue.push(GLYPHS[i]);
                if (i === targetIndex) break;
                i = (i + 1) % n;
            }
        } else {
            // Far: 2 evenly-spaced intermediates + target — looks like a quick mechanical spin
            queue.push(
                GLYPHS[(startIndex + Math.ceil(fwdDist * 0.33)) % n],
                GLYPHS[(startIndex + Math.ceil(fwdDist * 0.67)) % n],
                GLYPHS[targetIndex],
            );
        }
        if (!isFlipping) scheduleNextFlip();
    });
});
```

Replace it entirely with:

```js
// Handle live value changes after initial mount.
let mounted = false;
$effect(() => {
    const target = targetGlyph;
    if (!mounted) { mounted = true; return; }
    untrack(() => {
        // Navigation swap: skip animation, snap directly.
        if (anim.snap) {
            queue.length = 0;
            if (flipTimer) { clearTimeout(flipTimer); flipTimer = null; }
            currentGlyph = target;
            nextGlyph = target;
            isFlipping = false;
            return;
        }
        // Theatrical: stagger flip start by column position (75ms per column).
        // Double-check anim.snap inside the callback — a sort click may fire
        // after the timeout is scheduled but before it fires.
        setTimeout(() => {
            if (disposed || anim.snap) return;
            const tail = queue.length > 0 ? queue[queue.length - 1] : currentGlyph;
            const startIndex = Math.max(0, GLYPHS.indexOf(tail));
            const targetIndex = Math.max(0, GLYPHS.indexOf(target));
            if (startIndex === targetIndex) return;
            const n = GLYPHS.length;
            const fwdDist = (targetIndex - startIndex + n) % n;
            if (fwdDist <= 3) {
                // Close: step directly (1–3 flips)
                let i = (startIndex + 1) % n;
                while (true) {
                    queue.push(GLYPHS[i]);
                    if (i === targetIndex) break;
                    i = (i + 1) % n;
                }
            } else {
                // Far: 3 evenly-spaced intermediates + target (theatrical)
                queue.push(
                    GLYPHS[(startIndex + Math.ceil(fwdDist * 0.25)) % n],
                    GLYPHS[(startIndex + Math.ceil(fwdDist * 0.5)) % n],
                    GLYPHS[(startIndex + Math.ceil(fwdDist * 0.75)) % n],
                    GLYPHS[targetIndex],
                );
            }
            if (!isFlipping) scheduleNextFlip();
        }, colIndex * 75);
    });
});
```

- [ ] **Step 3.2: Run tests — expect 5 Cell tests to pass, 1 Word test still failing**

```bash
cd apps/web && node --test tests/theatrical-animation.test.mjs
```

Expected: 5 pass (`colIndex prop`, `190ms`, `colIndex * 75`, `anim.snap double-check`, `3 intermediates`). The Word `colIndex` test still fails.

---

### Task 4: Wire `colIndex` from Word.svelte and Verify

**Files:**
- Modify: `apps/web/src/lib/components/flap/Word.svelte:19-27` (Cell render)

- [ ] **Step 4.1: Pass `colIndex` to Cell in Word.svelte**

In `apps/web/src/lib/components/flap/Word.svelte`, the Cell render currently reads:

```svelte
<Cell 
    value={char} 
    width={cellWidth} 
    height={cellHeight} 
    staggerIndex={rowIndex * 4 + baseColIndex + index}
    rowIndex={rowIndex}
/>
```

Change to:

```svelte
<Cell 
    value={char} 
    width={cellWidth} 
    height={cellHeight} 
    staggerIndex={rowIndex * 4 + baseColIndex + index}
    colIndex={baseColIndex + index}
    rowIndex={rowIndex}
/>
```

- [ ] **Step 4.2: Run all 6 theatrical tests — expect all to pass**

```bash
cd apps/web && node --test tests/theatrical-animation.test.mjs
```

Expected: 6/6 pass.

- [ ] **Step 4.3: Run all existing tests to confirm nothing regressed**

```bash
cd apps/web && node --test tests/board-sse-wiring.test.mjs tests/just-qualified-animation.test.mjs
```

Expected: all pass.

- [ ] **Step 4.4: Type-check**

```bash
cd apps/web && npx svelte-kit sync && npx svelte-check --tsconfig ./tsconfig.json 2>&1 | tail -20
```

Expected: 0 errors.

- [ ] **Step 4.5: Commit**

```bash
git add apps/web/src/lib/components/flap/Cell.svelte \
        apps/web/src/lib/components/flap/Word.svelte
git commit -m "feat(animation): theatrical split-flap — 190ms flip, 75ms col stagger, 3 intermediates"
```

---

## Manual Verification

After completing all tasks, start the dev server and verify:

```bash
cd apps/web && npm run dev
```

Open `http://localhost:5173`. With the board in off-season mode, simulate a live stat change by manually calling:

```bash
# From the repo root — push a test delta via the API
curl -X POST http://localhost:8000/api/board/test-delta \
  -H 'Content-Type: application/json' \
  -d '{"player_id": 1, "stat_value": 0.350}'
```

If the API doesn't support a test-delta endpoint, manually edit a player's `stat_value` in the database and verify the SSE stream picks it up.

**What to look for:**
- Rank cells (left) flip first, stat cells (right) flip last — you should see the cascade sweep left-to-right
- Each cell's flip is visibly slower (190ms vs previous 120ms)
- Switching views (Hitters → Pitchers) still snaps instantly — no theatrical animation fires
- Clicking a sort column header still snaps cell values instantly; rows glide to new positions
