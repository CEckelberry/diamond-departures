<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let { view = 'hitters' }: { view?: string } = $props();

	const HITTER_STATS = ['wRC+', 'OPS', 'HR', 'SB', 'WAR'];
	const PITCHER_STATS = ['ERA', 'FIP', 'K%', 'WHIP', 'WAR'];

	const derivedStats = $derived(view === 'pitchers' ? PITCHER_STATS : HITTER_STATS);
	const activeSort = $derived($page.url.searchParams.get('sort') ?? derivedStats[0]);

	function setSort(stat: string) {
		const params = new URLSearchParams($page.url.searchParams);
		params.set('sort', stat);
		const search = params.toString();
		void goto(search ? `${$page.url.pathname}?${search}` : $page.url.pathname, {
			replaceState: true,
			keepFocus: true,
			noScroll: true
		});
	}
</script>

<div class="stat-picker" role="toolbar" aria-label="Stat picker">
	{#each derivedStats as stat}
		<button class:active={stat === activeSort} type="button" onclick={() => setSort(stat)}>{stat}</button>
	{/each}
</div>

<style>
	.stat-picker {
		display: flex;
		gap: 0.45rem;
		overflow-x: auto;
		padding-bottom: 0.15rem;
		scrollbar-width: thin;
	}

	button {
		flex: none;
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.74rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		padding: 0.35rem 0.6rem;
		border-radius: 0.4rem;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 22%, transparent);
		background: color-mix(in oklab, var(--chrome-bg) 70%, black);
		cursor: pointer;
		color: var(--chrome-text);
	}

	button.active {
		border-color: color-mix(in oklab, var(--cell-text) 55%, transparent);
		color: var(--cell-text);
	}
</style>
