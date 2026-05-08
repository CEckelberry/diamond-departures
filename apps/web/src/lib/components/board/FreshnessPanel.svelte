<script lang="ts">
	import { onMount } from 'svelte';

	type IngestRun = { run_id: string; started_at: string; status: string };
	type StatFreshness = { updated_at?: string; age_seconds?: number };
	type FreshnessPayload = {
		ingest_runs?: IngestRun[];
		schema_drift?: Record<string, unknown>;
		stats?: Record<string, StatFreshness>;
	};

	let {
		open = false,
		onclose
	}: {
		open?: boolean;
		onclose?: () => void;
	} = $props();

	let loading = $state(false);
	let error = $state('');
	let payload = $state<FreshnessPayload>({});

	const ingestRuns = $derived((payload.ingest_runs ?? []).slice(0, 10));
	const statEntries = $derived(Object.entries(payload.stats ?? {}));
	const schemaDrift = $derived(payload.schema_drift ?? { status: 'unknown' });

	function dotClass(ageSeconds: number | undefined): string {
		if (typeof ageSeconds !== 'number') return 'dot old';
		if (ageSeconds <= 120) return 'dot fresh';
		if (ageSeconds <= 600) return 'dot stale';
		return 'dot old';
	}

	function close() {
		onclose?.();
	}

	function onKeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') {
			event.preventDefault();
			close();
		}
	}

	async function loadFreshness() {
		loading = true;
		error = '';
		try {
			const response = await fetch('/api/freshness');
			if (!response.ok) throw new Error(`freshness-${response.status}`);
			payload = (await response.json()) as FreshnessPayload;
		} catch (cause: unknown) {
			error = cause instanceof Error ? cause.message : 'unable to load freshness';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		if (open) void loadFreshness();
	});

	$effect(() => {
		if (open) void loadFreshness();
	});
</script>

{#if open}
	<div class="overlay">
		<div
			class="panel"
			role="dialog"
			aria-label="Freshness debug panel"
			aria-modal="true"
			tabindex="-1"
			onkeydown={onKeydown}
		>
			<header>
				<h2>Freshness debug panel</h2>
				<button type="button" onclick={close} aria-label="Close freshness panel">Close</button>
			</header>

			{#if loading}
				<p>Loading freshness…</p>
			{:else if error}
				<p>{error}</p>
			{:else}
				<section aria-label="Last ingest runs">
					<h3>Last ingest runs</h3>
					<ul>
						{#each ingestRuns as run}
							<li>{run.started_at} · {run.status} · {run.run_id}</li>
						{/each}
					</ul>
				</section>

				<section aria-label="Per-stat freshness">
					<h3>Per-stat freshness</h3>
					<ul>
						{#each statEntries as [name, stat]}
							<li>
								<span class={dotClass(stat.age_seconds)} aria-hidden="true"></span>
								<strong>{name}</strong> — {stat.age_seconds ?? 'n/a'}s
							</li>
						{/each}
					</ul>
				</section>

				<section aria-label="Schema drift">
					<h3>Schema drift</h3>
					<pre>{JSON.stringify(schemaDrift, null, 2)}</pre>
				</section>
			{/if}
		</div>
	</div>
{/if}

<style>
	.overlay {
		position: fixed;
		inset: 0;
		background: color-mix(in oklab, black 48%, transparent);
		display: grid;
		place-items: center;
		padding: 1rem;
		z-index: 40;
	}

	.panel {
		width: min(780px, 100%);
		max-height: 86vh;
		overflow: auto;
		padding: 0.9rem;
		border-radius: 0.6rem;
		background: color-mix(in oklab, var(--board-bg) 95%, black);
		border: 1px solid color-mix(in oklab, var(--chrome-text) 20%, transparent);
	}

	header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 0.6rem;
	}

	h2,
	h3 {
		margin: 0;
	}

	ul {
		margin: 0.4rem 0 0;
		padding-left: 1rem;
	}

	.dot {
		display: inline-block;
		width: 0.55rem;
		height: 0.55rem;
		border-radius: 999px;
		margin-right: 0.35rem;
	}

	.dot.fresh {
		background: #22c55e;
	}

	.dot.stale {
		background: #f59e0b;
	}

	.dot.old {
		background: #ef4444;
	}
</style>
