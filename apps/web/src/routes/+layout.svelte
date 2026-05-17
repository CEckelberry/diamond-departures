<script lang="ts">
	import { onMount } from 'svelte';
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import Nav from '$lib/components/shell/Nav.svelte';
	import Footer from '$lib/components/shell/Footer.svelte';
	import SEO from '$lib/components/shell/SEO.svelte';
	import { einkStore } from '$lib/stores/eink';

	let { children } = $props();

	onMount(() => {
		einkStore.init();
	});
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
