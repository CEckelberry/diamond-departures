<script lang="ts">
	import SEO from '$lib/components/shell/SEO.svelte';
</script>

<SEO
	title="Diamond Departures · Methodology"
	description="Data sources, stat formulas, and known limits behind the Diamond Departures board."
	path="/methodology"
/>

<article class="methodology">
	<h1>Methodology</h1>
	<p>
		Diamond Departures combines MLB feed data with derived fantasy-oriented trend metrics. We optimize for
		transparent calculations and explainability over black-box ranking.
	</p>

	<section>
		<h2>Data sources</h2>
		<p>
			The ingest pipeline consumes official MLB game and player endpoints, then normalizes the payload into
			our snapshot + delta board model.
		</p>
		<p>
			Read full source notes in <a href="https://github.com/CEckelberry/diamond-departures/blob/main/DATA.md">DATA.md</a>.
		</p>
	</section>

	<section>
		<h2>Stat formulas</h2>
		<p>
			Board stats are calculated from a curated formula set tuned for in-season movement visibility.
		</p>
		<p>
			Formula details live in <a href="https://github.com/CEckelberry/diamond-departures/blob/main/STATS.md">STATS.md</a>.
		</p>
	</section>

	<section>
		<h2>Limits</h2>
		<ul>
			<li>Not every role has equivalent stat coverage at every update interval.</li>
			<li>Qualification transitions can briefly lag during API interruptions.</li>
			<li>The board is trend-focused, not a full projection engine.</li>
		</ul>
	</section>

	<section>
		<h2>Repository</h2>
		<p>
			For full docs, architecture notes, and task packets, see the
			<a href="https://github.com/CEckelberry/diamond-departures">GitHub repository</a>.
		</p>
	</section>
</article>

<style>
	.methodology {
		display: grid;
		gap: 1rem;
		max-width: 760px;
		line-height: 1.55;
	}

	h1,
	h2 {
		font-family: 'Instrument Serif', serif;
		margin: 0;
	}

	h1 {
		font-size: clamp(2rem, 5vw, 2.8rem);
	}

	h2 {
		font-size: 1.4rem;
	}

	a {
		color: color-mix(in oklab, var(--cell-text) 78%, white);
	}
</style>
