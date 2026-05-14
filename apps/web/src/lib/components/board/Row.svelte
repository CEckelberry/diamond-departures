<script lang="ts">
	import Word from "$lib/components/flap/Word.svelte";
	import { page } from "$app/stores";

	let { row, boardStyle = "sabermetric", rowIndex = 0 } = $props();

	const isPitcher = $derived(row.position === "SP" || row.position === "RP");
	const isDefense = $derived($page.url.searchParams.get("view") === "defense");
	const activeSort = $derived($page.url.searchParams.get("sort") ?? (isPitcher ? (boardStyle === "sabermetric" ? "FIP" : "W") : (boardStyle === "sabermetric" ? "wRC+" : "AVG")));

	const extraStatKeys = $derived((() => {
		if (isDefense) return boardStyle === "sabermetric" ? ["OAA", "UZR", "Def", "WAR", "DRS"] : ["Fielding %", "E", "PO", "A", "DP"];
		if (isPitcher) return boardStyle === "sabermetric" ? ["K/9", "BB/9", "FIP", "xFIP", "WAR"] : ["W", "L", "K", "ERA", "WHIP"];
		return boardStyle === "sabermetric" ? ["wRC+", "OPS+", "WAR", "DRS", "xwOBA"] : ["AVG", "HR", "RBI", "SB", "SLG"];
	})());

	function formatStat(key: string, val: any): string {
		if (val === undefined || val === null) return "---";
		const n = Number(val);
		if (["wRC+", "OPS+", "HR", "RBI", "SB", "W", "L", "K", "DRS", "H", "OAA", "E", "PO", "A", "DP", "Def", "UZR"].includes(key)) return String(Math.round(n));
		if (["AVG", "SLG", "OBP", "xwOBA", "Fielding %"].includes(key)) return n.toFixed(3).replace(/^0/, "");
		if (key === "WAR") return n.toFixed(1);
		if (["ERA", "WHIP", "FIP", "xFIP", "K/9", "BB/9"].includes(key)) return n.toFixed(2);
		if (key === "OPS") { const f = n.toFixed(3); return f.startsWith("0") ? f.replace(/^0/, "") : f; }
		return String(val);
	}
</script>

<div class="board-row">
	<div class="cell"><Word value={row.rank} width={3} cellWidth={16} cellHeight={26} rowIndex={rowIndex} baseColIndex={0} /></div>
	<div class="cell player"><Word value={row.player} width={18} cellWidth={16} cellHeight={26} rowIndex={rowIndex} baseColIndex={3} /></div>
	<div class="cell"><Word value={row.team} width={3} cellWidth={16} cellHeight={26} rowIndex={rowIndex} baseColIndex={21} /></div>
	<div class="cell"><Word value={row.position} width={2} cellWidth={16} cellHeight={26} rowIndex={rowIndex} baseColIndex={24} /></div>
	{#each extraStatKeys as key, i}
		<div class="cell" class:highlight={key === activeSort}><Word value={formatStat(key, row.stats[key])} width={key === "Fielding %" ? 6 : 4} cellWidth={16} cellHeight={26} rowIndex={rowIndex} baseColIndex={26 + i*5} /></div>
	{/each}
</div>

<style>
	.board-row { display: grid; grid-template-columns: 80px 1fr 100px 80px repeat(5, 120px); height: 32px; align-items: center; gap: 0.4rem; padding: 0.1rem 0.2rem; }
	.cell { display: flex; align-items: center; overflow: hidden; }
	.player { padding-left: 1.2rem; }
	.highlight :global(.cell) { --cell-text: #ffd700; }
</style>
