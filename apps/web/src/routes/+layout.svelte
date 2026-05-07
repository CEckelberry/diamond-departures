<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
	let theme = $state<'dark' | 'light'>('dark');

	function applyTheme(next: 'dark' | 'light') {
		theme = next;
		document.documentElement.dataset.theme = next;
	}

	function toggleTheme() {
		applyTheme(theme === 'dark' ? 'light' : 'dark');
	}

	$effect(() => {
		if (typeof window === 'undefined') return;
		const saved = window.localStorage.getItem('diamond-theme');
		if (saved === 'light' || saved === 'dark') {
			applyTheme(saved);
		} else {
			applyTheme('dark');
		}
	});

	$effect(() => {
		if (typeof window === 'undefined') return;
		window.localStorage.setItem('diamond-theme', theme);
	});
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<header class="chrome">
	<button class="theme-toggle" type="button" onclick={toggleTheme}>
		Toggle theme ({theme})
	</button>
</header>

{@render children()}
