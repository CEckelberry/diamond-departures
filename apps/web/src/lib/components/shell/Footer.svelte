<footer class="global-footer">
	<div class="inner">
		<span>Built with obsessive baseball nerdery.</span>
		<div class="links">
			<a href="/methodology">Methodology</a>
			<a href="https://github.com" rel="noreferrer" target="_blank">GitHub</a>
			<a href="/about">About</a>
		</div>
	</div>
</footer>

<style>
	.global-footer {
		margin-top: auto;
		border-top: 1px solid color-mix(in oklab, var(--chrome-text) 20%, transparent);
		background: color-mix(in oklab, var(--chrome-bg) 85%, transparent);
	}

	.inner {
		max-width: 1200px;
		margin: 0 auto;
		padding: 1.1rem 1rem 1.35rem;
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		justify-content: space-between;
		gap: 0.75rem;
		font-size: 0.8rem;
		color: color-mix(in oklab, var(--chrome-text) 70%, transparent);
	}

	.links {
		display: flex;
		gap: 0.8rem;
	}

	.links a {
		color: inherit;
		text-decoration: none;
	}

	.links a:hover {
		color: var(--cell-text);
	}
</style>
