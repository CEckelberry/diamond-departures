<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from "$app/stores";
	import { onMount, untrack } from "svelte";

	type ViewKey = "hitters" | "pitchers" | "defense" | "positions";
	type StyleKey = "sabermetric" | "traditional";

	const POSITIONS = ["C", "1B", "2B", "3B", "SS", "OF", "DH", "SP", "RP"];

	let dropdownOpen = $state(false);
	let dropdownRoot = $state<HTMLElement | null>(null);

	const currentView = $derived(($page.url.searchParams.get("view") as ViewKey | null) ?? "hitters");
	const currentStyle = $derived(($page.url.searchParams.get("style") as StyleKey | null) ?? "sabermetric");
	const currentPosition = $derived($page.url.searchParams.get("position") ?? "all");

	function syncParams(mutate: (params: URLSearchParams) => void) {
		const params = new URLSearchParams($page.url.searchParams);
		mutate(params);
		const search = params.toString();
		void goto(search ? `${$page.url.pathname}?${search}` : $page.url.pathname, {
			replaceState: false,
			keepFocus: true,
			noScroll: true
		});
	}

	function chooseView(next: ViewKey) {
		syncParams((params) => {
			params.set('view', next);
			if (next !== "positions") {
				params.delete('position');
			} else if (!params.get("position")) {
				params.set('position', 'all');
			}
			params.delete('sort');
		});
	}

	function chooseStyle(next: StyleKey) {
		syncParams((params) => {
			params.set('style', next);
			params.delete('sort');
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

<div class="controls-wrapper">
	<div class="view-tabs" role="tablist" aria-label="Leaderboard views">
		<button class:active={currentView === "hitters"} role="tab" onclick={() => chooseView("hitters")}>Hitters</button>
		<button class:active={currentView === "pitchers"} role="tab" onclick={() => chooseView("pitchers")}>Pitchers</button>
		<button class:active={currentView === "defense"} role="tab" onclick={() => chooseView("defense")}>Defense</button>

		<div class="positions" bind:this={dropdownRoot}>
			<button class:active={currentView === "positions" || currentPosition !== "all"} role="tab" onclick={toggleDropdown}>
				{currentPosition === "all" ? "Positions" : "Pos: " + currentPosition}
			</button>
			{#if dropdownOpen}
				<div class="menu" role="menu" aria-label="Position filter">
					{#each POSITIONS as position}
						<button role="menuitemradio" aria-checked={position === currentPosition} onclick={() => choosePosition(position)}>
							{position}
						</button>
					{/each}
				</div>
			{/if}
		</div>
	</div>

	<div class="sep"></div>

	<div class="style-tabs" role="tablist" aria-label="Stat styles">
		<button class:active={currentStyle === "sabermetric"} role="tab" onclick={() => chooseStyle("sabermetric")}>Saber</button>
		<button class:active={currentStyle === "traditional"} role="tab" onclick={() => chooseStyle("traditional")}>Traditional</button>
	</div>
</div>

<style>
	.controls-wrapper {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.sep {
		width: 1px;
		height: 1.2rem;
		background: color-mix(in oklab, var(--chrome-text) 15%, transparent);
	}

	.view-tabs, .style-tabs {
		display: flex;
		align-items: center;
		gap: 0.3rem;
	}

	button {
		font-family: "JetBrains Mono", monospace;
		font-size: 0.65rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		padding: 0.2rem 0.5rem;
		border-radius: 0.25rem;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 18%, transparent);
		background: color-mix(in oklab, var(--chrome-bg) 60%, black);
		color: color-mix(in oklab, var(--chrome-text) 80%, transparent);
		cursor: pointer;
	}

	button.active {
		background: var(--mlb-blue);
		border-color: var(--mlb-blue);
		color: white;
	}

	.positions {
		position: relative;
	}

	.menu {
		position: absolute;
		top: calc(100% + 0.35rem);
		right: 0;
		display: grid;
		gap: 0.2rem;
		padding: 0.35rem;
		border-radius: 0.4rem;
		min-width: 8rem;
		background: color-mix(in oklab, var(--board-bg) 92%, black);
		border: 1px solid color-mix(in oklab, var(--chrome-text) 16%, transparent);
		z-index: 20;
	}

	.menu button {
		border-radius: 0.25rem;
		text-align: left;
		text-transform: none;
	}
</style>
