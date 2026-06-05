<script lang="ts">
	import { page } from '$app/stores';
	import { createSupabaseBrowserClient } from '$lib/supabase';
	import { userStore } from '$lib/stores/user';

	const isActive = (path: string) => $page.url.pathname === path;

	async function signIn() {
		const supabase = createSupabaseBrowserClient();
		await supabase.auth.signInWithOAuth({
			provider: 'google',
			options: { redirectTo: `${$page.url.origin}/` },
		});
	}

	async function signOut() {
		const supabase = createSupabaseBrowserClient();
		await supabase.auth.signOut();
		userStore.set(null);
		window.location.href = '/';
	}
</script>

<nav class="site-nav">
	<div class="nav-inner">
		<div class="nav-left">
			<a href="/" class="wordmark" aria-label="Diamond Departures home">
				<span class="diamond">◈ Diamond</span><span class="departures"> Departures</span>
			</a>
			<a href="/" class:active={isActive('/')} class="nav-link">Leaderboard</a>
			<a href="/methodology" class:active={isActive('/methodology')} class="nav-link">Methodology</a>
			{#if $userStore?.is_premium}
				<a href="/boards" class:active={isActive('/boards')} class="nav-link">Boards</a>
			{/if}
		</div>

		<div class="nav-right">
			{#if $userStore}
				{#if !$userStore.is_premium}
					<a href="/upgrade" class="btn-primary">Go Premium</a>
				{/if}
				<button class="btn-avatar" type="button" onclick={signOut} title="Sign out ({$userStore.email})">
					{#if $userStore.avatar_url}
						<img src={$userStore.avatar_url} alt="avatar" class="avatar-img" />
					{:else}
						<span class="avatar-initials">{($userStore.name ?? $userStore.email).slice(0, 1).toUpperCase()}</span>
					{/if}
				</button>
			{:else}
				<button class="btn-outline" type="button" onclick={signIn}>Log in</button>
				<a href="/upgrade" class="btn-primary">Go Premium</a>
			{/if}
		</div>
	</div>
</nav>

<style>
	.site-nav {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 100;
		height: var(--nav-height, 2.75rem);
		background: color-mix(in oklab, var(--chrome-bg) 92%, transparent);
		border-bottom: 1px solid color-mix(in oklab, var(--chrome-text) 10%, transparent);
		backdrop-filter: blur(12px);
		-webkit-backdrop-filter: blur(12px);
	}

	.nav-inner {
		height: 100%;
		max-width: 1600px;
		margin: 0 auto;
		padding: 0 1rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.nav-left {
		display: flex;
		align-items: center;
		gap: 1.5rem;
	}

	.nav-right {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.wordmark {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.85rem;
		font-weight: 700;
		text-decoration: none;
		letter-spacing: 0.01em;
		white-space: nowrap;
	}

	.diamond { color: var(--mlb-red); }
	.departures { color: var(--chrome-text); }

	.nav-link {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.72rem;
		letter-spacing: 0.05em;
		color: color-mix(in oklab, var(--chrome-text) 50%, transparent);
		text-decoration: none;
		text-transform: uppercase;
		transition: color 0.15s;
	}

	.nav-link:hover,
	.nav-link.active { color: var(--chrome-text); }

	.btn-outline {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.7rem;
		letter-spacing: 0.04em;
		background: none;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 28%, transparent);
		border-radius: 0.3rem;
		color: color-mix(in oklab, var(--chrome-text) 75%, transparent);
		cursor: pointer;
		padding: 0.3rem 0.75rem;
		transition: border-color 0.15s, color 0.15s;
	}

	.btn-outline:hover {
		border-color: color-mix(in oklab, var(--chrome-text) 55%, transparent);
		color: var(--chrome-text);
	}

	.btn-primary {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.7rem;
		font-weight: 600;
		letter-spacing: 0.04em;
		background: var(--mlb-red);
		border: none;
		border-radius: 0.3rem;
		color: #fff;
		cursor: pointer;
		padding: 0.3rem 0.75rem;
		transition: opacity 0.15s;
		text-decoration: none;
	}

	.btn-primary:hover { opacity: 0.85; }

	.btn-avatar {
		background: none;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 20%, transparent);
		border-radius: 50%;
		cursor: pointer;
		width: 1.75rem;
		height: 1.75rem;
		padding: 0;
		overflow: hidden;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.avatar-img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		border-radius: 50%;
	}

	.avatar-initials {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.65rem;
		font-weight: 700;
		color: var(--chrome-text);
	}
</style>
