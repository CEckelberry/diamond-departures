<script lang="ts">
	import { onMount } from 'svelte';
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import Nav from '$lib/components/shell/Nav.svelte';
	import Footer from '$lib/components/shell/Footer.svelte';
	import SEO from '$lib/components/shell/SEO.svelte';
	import { einkStore } from '$lib/stores/eink';
	import { bigScreen, toggleBigScreen } from '$lib/stores/bigScreen';
	import { userStore } from '$lib/stores/user';

	let { children, data } = $props();

	$effect(() => {
		userStore.set(data.user ?? null);
	});

	let showHint = $state(false);
	let hintTimer: ReturnType<typeof setTimeout> | null = null;

	function handleKeydown(e: KeyboardEvent) {
		const tag = (e.target as HTMLElement)?.tagName;
		if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
		if (e.key === 'f' || e.key === 'F') {
			toggleBigScreen();
		}
	}

	async function enterFullscreen() {
		try {
			await document.documentElement.requestFullscreen();
		} catch {
			// browser denied or not supported — big screen CSS mode still applies
		}
	}

	function exitFullscreen() {
		if (document.fullscreenElement) {
			document.exitFullscreen().catch(() => {});
		}
	}

	// Sync fullscreen API with big screen store state
	let prevBigScreen = false;
	$effect(() => {
		const current = $bigScreen;
		if (current && !prevBigScreen) {
			enterFullscreen();
			showHint = true;
			if (hintTimer) clearTimeout(hintTimer);
			hintTimer = setTimeout(() => { showHint = false; }, 2500);
		} else if (!current && prevBigScreen) {
			exitFullscreen();
		}
		prevBigScreen = current;
	});

	// If user exits fullscreen via Escape, sync the store back to false
	function handleFullscreenChange() {
		if (!document.fullscreenElement && $bigScreen) {
			toggleBigScreen();
		}
	}

	onMount(() => {
		einkStore.init();
		document.addEventListener('fullscreenchange', handleFullscreenChange);
		return () => {
			document.removeEventListener('fullscreenchange', handleFullscreenChange);
			if (hintTimer) clearTimeout(hintTimer);
		};
	});
</script>

<svelte:window onkeydown={handleKeydown} />
<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<SEO
	title="Diamond Departures"
	description="Live fantasy baseball movement board for departures, trends, and qualification shifts."
	path="/"
/>

<div class="app-shell" class:big-screen={$bigScreen}>
	<Nav />

	<main class="shell-main">{@render children()}</main>

	<Footer />

	{#if $bigScreen}
		<div class="bs-header" aria-hidden="true">
			<div class="bs-logo">
				<span class="bs-diamond">◈ Diamond</span><span class="bs-departures"> Departures</span>
			</div>
			<div class="bs-rail"></div>
		</div>

		{#if showHint}
			<div class="bs-hint" role="status" aria-live="polite">Press <kbd>Esc</kbd> or <kbd>F</kbd> to exit</div>
		{/if}

		<button
			class="bs-exit"
			type="button"
			aria-label="Exit big screen"
			title="Exit big screen (F)"
			onclick={toggleBigScreen}
		>⊠</button>
	{/if}
</div>

<style>
	/* ── Big screen mode ───────────────────────────────────────────── */
	:global(:root) {
		--nav-height: 2.75rem;
	}

	.app-shell.big-screen :global(.site-nav) {
		transform: translateY(-100%);
		pointer-events: none;
	}

	.app-shell.big-screen :global(.global-footer) {
		display: none;
	}

	.app-shell.big-screen :global(.shell-main) {
		padding-top: var(--bs-header-height, 4rem);
	}

	.app-shell.big-screen :global(.top-bar) {
		display: none;
	}

	:global(.site-nav) {
		transition: transform 0.25s ease;
	}

	/* ── Big screen header zone ────────────────────────────────────── */
	.bs-header {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 90;
		pointer-events: none;
		display: flex;
		flex-direction: column;
		align-items: center;
		background: var(--board-bg);
		padding: 0.5rem 0 0;
	}

	.bs-logo {
		font-family: 'Instrument Serif', serif;
		font-size: clamp(1.2rem, 2vw, 1.8rem);
		font-weight: 400;
		letter-spacing: 0.02em;
		line-height: 1;
		white-space: nowrap;
		padding-bottom: 0.5rem;
	}

	.bs-diamond { color: var(--mlb-red); }
	.bs-departures { color: var(--chrome-text); }

	.bs-rail {
		width: 100%;
		height: 3px;
		background: linear-gradient(90deg, var(--mlb-blue) 0%, var(--mlb-blue) 50%, var(--mlb-red) 50%, var(--mlb-red) 100%);
		opacity: 0.85;
	}

	/* ── "Press F" hint ────────────────────────────────────────────── */
	.bs-hint {
		position: fixed;
		top: 0.75rem;
		left: 50%;
		transform: translateX(-50%);
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.7rem;
		letter-spacing: 0.05em;
		color: color-mix(in oklab, var(--chrome-text) 70%, transparent);
		background: color-mix(in oklab, var(--chrome-bg) 90%, transparent);
		border: 1px solid color-mix(in oklab, var(--chrome-text) 15%, transparent);
		border-radius: 0.35rem;
		padding: 0.35rem 0.75rem;
		backdrop-filter: blur(8px);
		z-index: 200;
		animation: hint-fade 2.5s ease forwards;
	}

	.bs-hint kbd {
		font-family: inherit;
		font-size: 0.7rem;
		background: color-mix(in oklab, var(--chrome-text) 12%, transparent);
		border: 1px solid color-mix(in oklab, var(--chrome-text) 25%, transparent);
		border-radius: 0.2rem;
		padding: 0.05rem 0.35rem;
	}

	@keyframes hint-fade {
		0%   { opacity: 0; transform: translateX(-50%) translateY(-4px); }
		15%  { opacity: 1; transform: translateX(-50%) translateY(0); }
		70%  { opacity: 1; }
		100% { opacity: 0; }
	}

	/* ── Exit button ───────────────────────────────────────────────── */
	.bs-exit {
		position: fixed;
		bottom: 1rem;
		right: 1rem;
		background: none;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 18%, transparent);
		border-radius: 0.3rem;
		color: color-mix(in oklab, var(--chrome-text) 35%, transparent);
		cursor: pointer;
		font-size: 1rem;
		line-height: 1;
		padding: 0.3rem 0.45rem;
		z-index: 200;
		transition: color 0.15s, border-color 0.15s;
	}

	.bs-exit:hover {
		color: var(--chrome-text);
		border-color: color-mix(in oklab, var(--chrome-text) 45%, transparent);
	}
</style>
