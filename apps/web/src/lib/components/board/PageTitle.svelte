<script lang="ts">
	let visible = $state(true);
</script>

{#if visible}
	<div class="title-row">
		<div class="title-spacer" aria-hidden="true"></div>
		<h1 class="site-title">
			<span class="word-diamond">Diamond</span>
			<span class="word-departures">Departures</span>
		</h1>
		<div class="title-actions">
			<button
				class="hide-btn"
				onclick={() => { visible = false; }}
				aria-label="Hide title"
				title="Hide title"
			>
				<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
					<polyline points="18 15 12 9 6 15"></polyline>
				</svg>
			</button>
		</div>
	</div>
{:else}
	<div class="restore-row">
		<button
			class="restore-btn"
			onclick={() => { visible = true; }}
			aria-label="Show Diamond Departures title"
			title="Show title"
		>
			◈
		</button>
	</div>
{/if}

<style>
	/* ── Visible title row ─────────────────────────────────────────── */
	.title-row {
		display: grid;
		grid-template-columns: 1fr auto 1fr;
		align-items: center;
		padding: 0.5rem 0.25rem 0.25rem;
	}

	.title-spacer {
		/* balances the hide button on the right so the title centres true */
	}

	.site-title {
		font-family: 'Instrument Serif', serif;
		font-size: clamp(2.2rem, 5vw, 4rem);
		font-weight: 400;
		letter-spacing: 0.02em;
		line-height: 1.1;
		margin: 0;
		text-align: center;
		white-space: nowrap;
	}

	.word-diamond {
		color: var(--mlb-red);
	}

	.word-departures {
		color: var(--chrome-text);
		margin-left: 0.35em;
	}

	.title-actions {
		display: flex;
		justify-content: flex-end;
		align-items: center;
	}

	.hide-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		background: none;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 20%, transparent);
		border-radius: 0.35rem;
		color: color-mix(in oklab, var(--chrome-text) 55%, transparent);
		cursor: pointer;
		padding: 0.3rem;
		transition: color 0.15s, border-color 0.15s;
		line-height: 0;
	}

	.hide-btn:hover {
		color: var(--chrome-text);
		border-color: color-mix(in oklab, var(--chrome-text) 45%, transparent);
	}

	/* ── Restore row (collapsed state) ────────────────────────────── */
	.restore-row {
		display: flex;
		justify-content: center;
		padding: 0.25rem 0;
	}

	.restore-btn {
		background: none;
		border: 1px solid color-mix(in oklab, var(--chrome-text) 20%, transparent);
		border-radius: 0.35rem;
		color: var(--mlb-red);
		cursor: pointer;
		font-size: 1rem;
		line-height: 1;
		padding: 0.2rem 0.5rem;
		transition: color 0.15s, border-color 0.15s;
	}

	.restore-btn:hover {
		border-color: var(--mlb-red);
		color: var(--mlb-red);
	}
</style>
