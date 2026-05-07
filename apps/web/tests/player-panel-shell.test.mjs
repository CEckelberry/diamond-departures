import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const pagePath = new URL("../src/routes/+page.svelte", import.meta.url);
const boardPath = new URL(
	"../src/lib/components/board/Board.svelte",
	import.meta.url,
);
const rowPath = new URL(
	"../src/lib/components/board/Row.svelte",
	import.meta.url,
);
const panelPath = new URL(
	"../src/lib/components/player/Panel.svelte",
	import.meta.url,
);

async function load(path) {
	return readFile(path, "utf8");
}

test("+page wires selected player state and renders Panel shell", async () => {
	const src = await load(pagePath);
	assert.match(
		src,
		/import\s+Panel\s+from\s+'\$lib\/components\/player\/Panel\.svelte'/,
	);
	assert.match(src, /selectedPlayer(Id)?\s*=\s*\$state/);
	assert.match(src, /<Panel\s+selectedPlayerId=\{selectedPlayer(Id)?\}/);
});

test("board rows expose click/select plumbing", async () => {
	const boardSrc = await load(boardPath);
	const rowSrc = await load(rowPath);
	assert.match(rowSrc, /onclick=/);
	assert.match(rowSrc, /playerId|row\.playerId/);
	assert.match(boardSrc, /onselect|on:select/);
	assert.match(boardSrc, /<Row\s+\{row\}/);
});

test("player panel contains empty, loading, and error shell states", async () => {
	const src = await load(panelPath);
	assert.match(src, /panel-empty|No player selected/);
	assert.match(src, /panel-loading|Loading player details/);
	assert.match(src, /panel-error|Unable to load player details/);
});
