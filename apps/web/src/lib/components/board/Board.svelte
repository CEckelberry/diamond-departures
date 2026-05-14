<script lang="ts">
	import { flip } from "svelte/animate";
	import { cubicOut } from "svelte/easing";
	import { goto } from "$app/navigation";
	import { page } from "$app/stores";
	import { playRowShift } from "$lib/audio/flap";
	import Row from "./Row.svelte";

	let { rows = [], view = "hitters" } = $props();

	const boardStyle = $derived($page.url.searchParams.get("style") ?? "sabermetric");
	const extraStats = $derived((() => {
		if (view === "defense") return boardStyle === "sabermetric" ? ["OAA", "UZR", "Def", "WAR", "DRS"] : ["Fielding %", "E", "PO", "A", "DP"];
		if (view.includes("pitcher")) return boardStyle === "sabermetric" ? ["K/9", "BB/9", "FIP", "xFIP", "WAR"] : ["W", "L", "K", "ERA", "WHIP"];
		return boardStyle === "sabermetric" ? ["wRC+", "OPS+", "WAR", "DRS", "xwOBA"] : ["AVG", "HR", "RBI", "SB", "SLG"];
	})());

	const activeSort = $derived($page.url.searchParams.get("sort") ?? (view.includes("pitcher") ? (boardStyle === "sabermetric" ? "FIP" : "W") : (boardStyle === "sabermetric" ? "wRC+" : "AVG")));

	function setSort(stat: string) {
		const params = new URLSearchParams($page.url.searchParams);
		params.set("sort", stat);
		goto(`${$page.url.pathname}?${params.toString()}`, { replaceState: false, noScroll: true });
	}

	let previousOrder = "";
	$effect(() => {
		const order = rows.map(r => r.playerId).join(",");
		if (previousOrder && order !== previousOrder) playRowShift();
		previousOrder = order;
	});
</script>

<section class="board">
	<div class="board-rail"></div>
	<div class="board-header-row">
		<span class="rk-head">RK</span><span>PLAYER</span><span>TEAM</span><span>POS</span>
		{#each extraStats as head}
			<button class="stat-head-btn" class:active={head === activeSort} onclick={() => setSort(head)}>{head}</button>
		{/each}
	</div>
	<div class="board-body">
		{#each rows as row, index (row.playerId)}
			<div class="row-shell" animate:flip={{delay: index * 10, duration: 300, easing: cubicOut}}>
				<Row {row} {boardStyle} rowIndex={index} />
			</div>
		{/each}
	</div>
</section>

<style>
	.board { position: relative; border-radius: 0.5rem; padding: 1rem 0.8rem 0.6rem; background: color-mix(in oklab, var(--board-bg) 92%, black); border: 1px solid color-mix(in oklab, var(--chrome-text) 18%, transparent); overflow: hidden; }
	.board-rail { position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, var(--mlb-blue) 0%, var(--mlb-blue) 50%, var(--mlb-red) 50%, var(--mlb-red) 100%); opacity: 0.8; }
	.board-header-row { display: grid; grid-template-columns: 80px 1fr 100px 80px repeat(5, 120px); gap: 0.4rem; border-bottom: 1px solid color-mix(in oklab, var(--chrome-text) 14%, transparent); font-family: "JetBrains Mono", monospace; font-size: 0.65rem; text-transform: uppercase; color: color-mix(in oklab, var(--chrome-text) 50%, transparent); padding-bottom: 0.5rem; margin-bottom: 0.5rem; }
	.rk-head { padding-left: 0.4rem; }
	.stat-head-btn { background: none; border: none; color: inherit; font: inherit; text-align: left; cursor: pointer; padding: 0; letter-spacing: inherit; text-transform: inherit; }
	.stat-head-btn.active { color: #ffd700; }
	.board-body { display: grid; gap: 0.25rem; max-height: 80vh; overflow: auto; }
</style>
