<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import Nav from '$lib/components/shell/Nav.svelte';
	import Footer from '$lib/components/shell/Footer.svelte';

	let { children } = $props();
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div class="app-shell">
	<Nav />
	<main class="shell-main">{@render children()}</main>
	<Footer />
</div>
