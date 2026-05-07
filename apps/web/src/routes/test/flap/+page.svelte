<script lang="ts">
	import { dev } from '$app/environment';
	import Cell from '$lib/components/flap/Cell.svelte';
	import Word from '$lib/components/flap/Word.svelte';
	import { playRowShift } from '$lib/audio/flap';
	import { setSoundEnabled, setSoundVolume, soundEnabled, soundVolume } from '$lib/stores/sound';

	const glyphs = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
	const words = ['98', '172', 'JUDGE, A.', 'SOTO, J.', '0.312'];

	let single = $state('8');
	let word = $state(words[0]);
	let wordIndex = $state(0);
	let storm = $state(Array.from({ length: 30 }, () => randomGlyph()));
	let runningScenario = $state(false);

	function randomGlyph() {
		return glyphs[Math.floor(Math.random() * glyphs.length)] ?? ' ';
	}

	function flipSingle() {
		single = randomGlyph();
	}

	function flipWord() {
		wordIndex = (wordIndex + 1) % words.length;
		word = words[wordIndex] ?? words[0];
	}

	function flipStorm() {
		storm = Array.from({ length: 30 }, () => randomGlyph());
	}

	async function runScenario() {
		if (runningScenario) return;
		runningScenario = true;
		setSoundEnabled(true);
		setSoundVolume(0.3);

		for (let i = 0; i < 4; i += 1) {
			flipSingle();
			flipWord();
			flipStorm();
			if (i === 2) playRowShift();
			await new Promise((resolve) => setTimeout(resolve, 600));
		}

		runningScenario = false;
	}
</script>

{#if dev}
	<main class="page">
		<h1>Split-flap test page</h1>

		<section class="controls">
			<button id="single" type="button" onclick={flipSingle}>Flip single cell</button>
			<button id="word" type="button" onclick={flipWord}>Flip word</button>
			<button id="storm" type="button" onclick={flipStorm}>Flip 30 cells</button>
			<button id="row-shift" type="button" onclick={playRowShift}>Play row-shift sound</button>
		</section>

		<section class="sound">
			<label>
				<input
					type="checkbox"
					checked={$soundEnabled}
					onchange={(event) => setSoundEnabled((event.currentTarget as HTMLInputElement).checked)}
				/>
				Sound enabled
			</label>
			<label>
				Volume
				<input
					type="range"
					min="0"
					max="1"
					step="0.05"
					value={$soundVolume}
					oninput={(event) => setSoundVolume(Number((event.currentTarget as HTMLInputElement).value))}
				/>
			</label>
		</section>

		<section class="demo">
			<h2>Single cell</h2>
			<Cell value={single} />
		</section>

		<section class="demo">
			<h2>Word</h2>
			<Word value={word} width={12} />
		</section>

		<section class="demo">
			<h2>Storm (30 cells)</h2>
			<div class="storm-grid">
				{#each storm as glyph, index (index)}
					<Cell value={glyph} />
				{/each}
			</div>
		</section>

		<section class="demo">
			<h2>Scenarios</h2>
			<button type="button" onclick={runScenario} disabled={runningScenario}>
				{runningScenario ? 'Running scenario...' : 'Run mixed scenario'}
			</button>
		</section>
	</main>
{:else}
	<main class="page"><p>Flap test page available only in dev builds.</p></main>
{/if}

<style>
	.page {
		display: grid;
		gap: 1rem;
		padding: 1.5rem;
	}

	.controls,
	.sound {
		display: flex;
		gap: 0.75rem;
		flex-wrap: wrap;
	}

	button,
	input {
		font-family: 'JetBrains Mono', monospace;
	}

	.storm-grid {
		display: grid;
		grid-template-columns: repeat(10, max-content);
		gap: 0.35rem;
	}
</style>
