<script lang="ts">
	let {
		title,
		description,
		path = '/',
		image = '/og/top3.svg'
	}: {
		title: string;
		description: string;
		path?: string;
		image?: string;
	} = $props();

	const siteName = 'Diamond Departures';
	const absoluteUrl = $derived(`https://diamond-departures.app${path}`);
	const absoluteImage = $derived(
		image.startsWith('http') ? image : `https://diamond-departures.app${image}`
	);
</script>

<svelte:head>
	<title>{title}</title>
	<meta name="description" content={description} />
	<meta property="og:site_name" content={siteName} />
	<meta property="og:title" content={title} />
	<meta property="og:description" content={description} />
	<meta property="og:type" content="website" />
	<meta property="og:url" content={absoluteUrl} />
	<meta property="og:image" content={absoluteImage} />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content={title} />
	<meta name="twitter:description" content={description} />
	<meta name="twitter:image" content={absoluteImage} />
</svelte:head>
