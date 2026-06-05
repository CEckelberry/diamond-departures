<!-- src/routes/upgrade/success/+page.svelte -->
<script lang="ts">
	import SEO from '$lib/components/shell/SEO.svelte';
</script>

<SEO title="Welcome to Premium — Diamond Departures" description="" path="/upgrade/success" />

<div class="success-page">
	<div class="card">
		<div class="icon">◈</div>
		<h1 class="title">You're Premium.</h1>
		<p class="body">Your purchase is confirmed. Premium features are now active — sign in to access your watchlist, watch boards, and alerts.</p>
		<a href="/" class="home-btn">Back to the board</a>
	</div>
</div>

<style>
	.success-page {
		min-height: calc(100vh - var(--nav-height));
		display: flex; align-items: center; justify-content: center;
		padding: calc(var(--nav-height) + 2rem) 2rem 2rem;
	}
	.card {
		background: var(--chrome-bg);
		border: 1px solid color-mix(in oklab, var(--chrome-text) 12%, transparent);
		border-radius: 0.75rem; padding: 2.5rem; max-width: 380px; width: 100%;
		text-align: center; display: flex; flex-direction: column; gap: 1rem;
	}
	.icon { font-size: 2rem; color: var(--mlb-red); }
	.title { font-family: 'Instrument Serif', serif; font-size: 1.4rem; font-weight: 400; margin: 0; color: var(--chrome-text); }
	.body { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: color-mix(in oklab, var(--chrome-text) 65%, transparent); margin: 0; line-height: 1.6; }
	.home-btn {
		background: var(--mlb-red); color: #fff; border: none; border-radius: 0.4rem;
		font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; font-weight: 700;
		padding: 0.55rem 1.5rem; text-decoration: none; transition: opacity 0.15s;
	}
	.home-btn:hover { opacity: 0.85; }
</style>
