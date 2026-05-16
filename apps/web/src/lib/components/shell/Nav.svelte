<nav class="global-nav" aria-label="Primary">
	<div class="inner">
		<a class="brand" href="/">Diamond Departures</a>
		<div class="links">
			<a href="/case-study">Case Study</a>
			<a href="https://github.com" rel="noreferrer" target="_blank">GitHub</a>
			<a href="https://cole.codes" rel="noreferrer" target="_blank">Back to Portfolio</a>
		</div>
	</div>
</nav>

<style>
	.global-nav {
		position: fixed;
		top: 0;
		left: 0;
		right: 0;
		z-index: 40;
		background: color-mix(in oklab, var(--chrome-bg) 92%, transparent);
		backdrop-filter: blur(8px);
		border-bottom: 1px solid color-mix(in oklab, var(--chrome-text) 20%, transparent);
	}

	.inner {
		max-width: 1200px;
		margin: 0 auto;
		padding: 0.9rem 1rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 0.75rem;
	}

	.brand {
		font-family: 'Instrument Serif', serif;
		font-size: clamp(1.1rem, 1.8vw, 1.5rem);
		color: var(--mlb-red); font-weight: 700;
		text-decoration: none;
	}

	.links {
		display: flex;
		flex-wrap: wrap;
		gap: 0.75rem;
	}

	.links a {
		font-family: 'JetBrains Mono', monospace;
		font-size: 0.78rem;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: color-mix(in oklab, var(--chrome-text) 88%, transparent);
		text-decoration: none;
	}

	.links a:hover {
		color: var(--cell-text);
	}
</style>
