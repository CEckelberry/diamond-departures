import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const panelPath = new URL(
	"../src/lib/components/player/Panel.svelte",
	import.meta.url,
);
const chartPath = new URL(
	"../src/lib/components/player/TrendChart.svelte",
	import.meta.url,
);

async function load(path) {
	return readFile(path, "utf8");
}

test("panel fetches player history with stat query and tracks history state", async () => {
	const src = await load(panelPath);
	assert.match(
		src,
		/\/api\/players\/\$\{selectedPlayerId\}\/history\?stat=\$\{encodeURIComponent\(trendStat\)\}/,
	);
	assert.match(src, /historyPoints\s*=\s*\$state/);
	assert.match(src, /historyLoading\s*=\s*\$state/);
	assert.match(src, /historyError\s*=\s*\$state/);
});

test("trend chart component renders svg sparkline shell", async () => {
	const src = await load(chartPath);
	assert.match(src, /<svg[^>]*aria-label=['"]Player trend chart['"]/);
	assert.match(src, /<polyline/);
	assert.match(src, /points=/);
	assert.match(src, /trend-stat|chart-caption/);
});

test("panel renders trend chart with points and stat", async () => {
	const src = await load(panelPath);
	assert.match(
		src,
		/import\('\.\/TrendChart\.svelte'\)|import\s+TrendChart\s+from\s+'\.\/TrendChart\.svelte'/,
	);
	assert.match(
		src,
		/<svelte:component\s+this=\{TrendChart\}\s+points=\{historyPoints\}\s+stat=\{trendStat\}|<TrendChart\s+points=\{historyPoints\}\s+stat=\{trendStat\}/,
	);
});
