<script lang="ts">
	import '../../app.css';
	import { einkStore } from '$lib/stores/eink';
	import { onMount } from 'svelte';
	let { children } = $props();
	onMount(() => einkStore.init());
</script>

<svelte:head><title>Flap Lab · Diamond Departures</title></svelte:head>
{@render children()}
