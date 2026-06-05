<script lang="ts">
	import { page } from '$app/stores';

	const isActive = (path: string) => $page.url.pathname === path;
</script>

<nav class="site-nav">
	<div class="nav-inner">
		<div class="nav-left">
			<a href="/" class="wordmark" aria-label="Diamond Departures home">
				<span class="diamond">◈ Diamond</span><span class="departures"> Departures</span>
			</a>
			<a href="/" class:active={isActive('/')} class="nav-link">Leaderboard</a>
			<a href="/methodology" class:active={isActive('/methodology')} class="nav-link">Methodology</a>
		</div>

		<div class="nav-right">
			<!-- Auth buttons — wired up when backend is ready -->
			<button class="btn-outline" type="button">Log in</button>
			<button class="btn-primary" type="button">Go Premium</button>
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

	.diamond {
		color: var(--mlb-red);
	}

	.departures {
		color: var(--chrome-text);
	}

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
	.nav-link.active {
		color: var(--chrome-text);
	}

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
	}

	.btn-primary:hover {
		opacity: 0.85;
	}
</style>
