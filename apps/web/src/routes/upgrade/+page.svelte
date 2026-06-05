<!-- src/routes/upgrade/+page.svelte -->
<script lang="ts">
	import { userStore } from '$lib/stores/user';
	import SEO from '$lib/components/shell/SEO.svelte';

	let loading = $state(false);
	let error = $state('');

	async function startCheckout() {
		loading = true;
		error = '';
		try {
			const resp = await fetch('/api/creem/checkout', { method: 'POST' });
			if (!resp.ok) {
				error = resp.status === 401 ? 'Please sign in first.' : 'Something went wrong. Try again.';
				return;
			}
			const { checkout_url } = await resp.json();
			window.location.href = checkout_url;
		} catch {
			error = 'Network error. Try again.';
		} finally {
			loading = false;
		}
	}
</script>

<SEO title="Upgrade — Diamond Departures" description="Get lifetime access to premium features." path="/upgrade" />

<div class="upgrade-page">
	<div class="card">
		<div class="logo">◈</div>
		<h1 class="title">Diamond Departures Premium</h1>
		<p class="subtitle">One-time purchase. Yours forever.</p>

		<ul class="features">
			<li>⊕ Player Watchlist — pin players across all views</li>
			<li>⊕ Custom Watch Boards — build boards from any players</li>
			<li>⊕ Email Alerts — get notified when stats cross thresholds</li>
			<li>⊕ CSV Export — download any leaderboard</li>
		</ul>

		<div class="price">$5.99 <span class="price-sub">once, forever</span></div>

		{#if $userStore?.is_premium}
			<div class="already">You already have Premium. ◈</div>
		{:else}
			<button class="checkout-btn" onclick={startCheckout} disabled={loading}>
				{loading ? 'Redirecting...' : 'Get Premium'}
			</button>
			{#if error}<p class="err">{error}</p>{/if}
		{/if}
	</div>
</div>

<style>
	.upgrade-page {
		min-height: calc(100vh - var(--nav-height));
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 2rem 1rem;
		padding-top: calc(var(--nav-height) + 2rem);
	}
	.card {
		background: var(--chrome-bg);
		border: 1px solid color-mix(in oklab, var(--chrome-text) 12%, transparent);
		border-radius: 0.75rem;
		padding: 2.5rem;
		max-width: 420px;
		width: 100%;
		text-align: center;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}
	.logo { font-size: 2rem; color: var(--mlb-red); }
	.title { font-family: 'Instrument Serif', serif; font-size: 1.5rem; font-weight: 400; margin: 0; color: var(--chrome-text); }
	.subtitle { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: color-mix(in oklab, var(--chrome-text) 55%, transparent); margin: 0; }
	.features { list-style: none; padding: 0; margin: 0; text-align: left; display: flex; flex-direction: column; gap: 0.5rem; }
	.features li { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: color-mix(in oklab, var(--chrome-text) 75%, transparent); }
	.price { font-family: 'JetBrains Mono', monospace; font-size: 1.75rem; font-weight: 700; color: var(--chrome-text); }
	.price-sub { font-size: 0.8rem; font-weight: 400; color: color-mix(in oklab, var(--chrome-text) 50%, transparent); }
	.checkout-btn {
		background: var(--mlb-red); color: #fff; border: none; border-radius: 0.4rem;
		font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 700;
		letter-spacing: 0.04em; padding: 0.65rem 2rem; cursor: pointer;
		transition: opacity 0.15s; width: 100%;
	}
	.checkout-btn:hover:not(:disabled) { opacity: 0.85; }
	.checkout-btn:disabled { opacity: 0.5; cursor: not-allowed; }
	.err { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: var(--mlb-red); margin: 0; }
	.already { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: color-mix(in oklab, var(--chrome-text) 65%, transparent); }
</style>
