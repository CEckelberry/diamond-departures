<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { onMount } from 'svelte';

	type ViewKey = 'hitters' | 'pitchers' | 'positions';

	const POSITIONS = ['all', 'C', '1B', '2B', '3B', 'SS', 'OF', 'DH', 'SP', 'RP'];

	let dropdownOpen = $state(false);
	let dropdownRoot = $state<HTMLElement | null>(null);

	const view = $derived(($page.url.searchParams.get('view') as ViewKey | null) ?? 'hitters');
	const activePosition = $derived($page.url.searchParams.get('position') ?? 'all');

	function syncParams(mutate: (params: URLSearchParams) => void) {
		const params = new URLSearchParams($page.url.searchParams);
		mutate(params);
		const search = params.toString();
		void goto(search ? `${$page.url.pathname}?${search}` : $page.url.pathname, {
			replaceState: true,
			keepFocus: true,
			noScroll: true
		});
	}

	function chooseView(next: ViewKey) {
		syncParams((params) => {
			params.set('view', next);
			if (next !== 'positions') {
				params.delete('position');
			} else if (!params.get('position')) {
				params.set('position', 'all');
			}
		});
	}

	function choosePosition(position: string) {
		syncParams((params) => {
			params.set('view', 'positions');
			params.set('position', position);
		});
		dropdownOpen = false;
	}

	function toggleDropdown() {
		dropdownOpen = !dropdownOpen;
		if (!dropdownOpen) return;
		chooseView('positions');
	}

	onMount(() => {
		const closeOnOutsideClick = (event: MouseEvent) => {
			if (!dropdownOpen) return;
			if (!(event.target instanceof Node)) return;
			if (dropdownRoot?.contains(event.target)) return;
			dropdownOpen = false;
		};

		document.addEventListener('click', closeOnOutsideClick);
		return () => document.removeEventListener('click', closeOnOutsideClick);
	});
</script>

<div class="view-tabs" role="tablist" aria-label="Leaderboard views">
	<button class:active={view === 'hitters'} role="tab" onclick={() => chooseView('hitters')}>Hitters</button>
	<button class:active={view === 'pitchers'} role="tab" onclick={() => chooseView('pitchers')}>Pitchers</button>

	<div class="positions" bind:this={dropdownRoot}>
		<button class:active={view === 'positions'} role="tab" onclick={toggleDropdown}>
			Positions ({activePosition})
		</button>
		{#if dropdownOpen}
			<div class="menu" role="menu" aria-label="Position filter">
				{#each POSITIONS as position}
					<button role="menuitemradio" aria-checked={position === activePosition} onclick={() => choosePosition(position)}>
						{position}
					</button>
				{/each}
			</div>
		{/if}
	</div>
</div>

<style>
	.view-tabs {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex-wrap: wrap;
	}

	.view-tabs > button,
	.positions > button,
	.menu button {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.74rem;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		padding: 0.4rem 0.68rem;
		border-radius: 999px;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 22%, transparent);
		background: color-mix(in oklab, var(--chrome-bg) 75%, black);
		color: var(--chrome-text);
		cursor: pointer;
	}

	button.active {
		border-color: color-mix(in oklab, var(--cell-text) 50%, transparent);
		color: var(--cell-text);
	}

	.positions {
		position: relative;
	}

	.menu {
		position: absolute;
		top: calc(100% + 0.35rem);
		right: 0;
		display: grid;
		gap: 0.3rem;
		padding: 0.4rem;
		border-radius: 0.5rem;
		min-width: 6rem;
		background: color-mix(in oklab, var(--board-bg) 86%, black);
		border: 1px solid color-mix(in oklab, var(--chrome-text) 20%, transparent);
		z-index: 20;
	}

	.menu button {
		border-radius: 0.35rem;
		text-align: left;
		text-transform: none;
	}
</style>
