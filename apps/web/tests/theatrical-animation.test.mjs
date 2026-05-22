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
