<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	let { view = 'hitters', style = 'sabermetric' }: { view?: string; style?: string } = $props();

	const HITTER_SABER_STATS = ['wOBA', 'wRC+', 'BABIP', 'ISO', 'BB%', 'K%', 'OPS'];
	const HITTER_TRAD_STATS  = ['AVG', 'HR', 'RBI', 'OBP', 'SLG', 'SB', 'OPS'];
	const HITTER_STATCAST_STATS = ['xwOBA', 'xBA', 'barrel_pct', 'hard_hit_pct', 'exit_velocity'];
	const PITCHER_SABER_STATS = ['FIP', 'K-BB%', 'K%', 'BB%', 'ERA', 'WHIP', 'K/9'];
	const PITCHER_TRAD_STATS  = ['ERA', 'W', 'WHIP', 'K', 'SV', 'BB/9'];

	const derivedStats = $derived(
		view.startsWith('pitcher')
			? (style === 'traditional' ? PITCHER_TRAD_STATS : PITCHER_SABER_STATS)
			: style === 'statcast'
				? HITTER_STATCAST_STATS
				: style === 'traditional'
					? HITTER_TRAD_STATS
					: HITTER_SABER_STATS
	);
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
		gap: 0.35rem;
		overflow-x: auto;
		scrollbar-width: none;
		-ms-overflow-style: none;
	}

	.stat-picker::-webkit-scrollbar {
		display: none;
	}

	button {
		flex: none;
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.68rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		padding: 0.25rem 0.55rem;
		border-radius: 0.3rem;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 18%, transparent);
		background: color-mix(in oklab, var(--chrome-bg) 60%, black);
		cursor: pointer;
		color: color-mix(in oklab, var(--chrome-text) 80%, transparent);
	}

	button.active {
		background: color-mix(in oklab, var(--cell-bg) 40%, var(--chrome-bg));
		border-color: var(--mlb-blue); background: var(--mlb-blue);
		color: var(--cell-text);
	}
</style>
