<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import Nav from '$lib/components/shell/Nav.svelte';
	import Footer from '$lib/components/shell/Footer.svelte';
	import SEO from '$lib/components/shell/SEO.svelte';

	let { children } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
<SEO
	title="Diamond Departures"
	description="Live fantasy baseball movement board for departures, trends, and qualification shifts."
	path="/"
/>

<div class="app-shell">
	<Nav />
	<main class="shell-main">{@render children()}</main>
	<Footer />
</div>
