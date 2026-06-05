<!-- src/lib/components/auth/PremiumGate.svelte -->
<script lang="ts">
	import { userStore } from '$lib/stores/user';

	let { children, feature = 'This feature' }: { children: any; feature?: string } = $props();
</script>

{#if $userStore?.is_premium}
	{@render children()}
{:else}
	<div class="gate">
		<div class="gate-icon">◈</div>
		<p class="gate-text">{feature} is available to Premium members.</p>
		<a href="/upgrade" class="gate-btn">Upgrade for $5.99</a>
		{#if !$userStore}
			<p class="gate-sub">Already purchased? <a href="/upgrade" class="gate-signin">Sign in</a></p>
		{/if}
	</div>
{/if}

<style>
	.gate {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.75rem;
		padding: 2rem;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 12%, transparent);
		border-radius: 0.5rem;
		text-align: center;
		font-family: 'JetBrains Mono', monospace;
	}
	.gate-icon { font-size: 1.5rem; color: var(--mlb-red); }
	.gate-text { font-size: 0.8rem; color: color-mix(in oklab, var(--chrome-text) 70%, transparent); margin: 0; }
	.gate-btn {
		background: var(--mlb-red);
		color: #fff;
		border: none;
		border-radius: 0.3rem;
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.75rem;
		font-weight: 600;
		letter-spacing: 0.04em;
		padding: 0.4rem 1rem;
		text-decoration: none;
		cursor: pointer;
		transition: opacity 0.15s;
	}
	.gate-btn:hover { opacity: 0.85; }
	.gate-sub { font-size: 0.7rem; color: color-mix(in oklab, var(--chrome-text) 45%, transparent); margin: 0; }
	.gate-signin { color: var(--chrome-text); text-decoration: underline; }
</style>
