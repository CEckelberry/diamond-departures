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
