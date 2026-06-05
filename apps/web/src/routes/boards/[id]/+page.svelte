<script lang="ts">
    import SEO from '$lib/components/shell/SEO.svelte';

    let { data } = $props();
</script>

<SEO title="{data.board.name} — Diamond Departures" description="Your custom watch board." path="/boards/{data.board.id}" />

<div class="board-page">
    <div class="top-bar">
        <a href="/boards" class="back-link">← Boards</a>
        <h1 class="board-title">{data.board.name}</h1>
    </div>

    {#if data.board.players.length === 0}
        <p class="empty">No players added yet. Pin players from the main board using the ⊕ icon.</p>
    {:else}
        <p class="info">Showing {data.board.players.length} player{data.board.players.length !== 1 ? 's' : ''} on this board.</p>
    {/if}
</div>

<style>
    .board-page { padding: calc(var(--nav-height) + 2rem) 1rem 2rem; max-width: 1600px; margin: 0 auto; }
    .top-bar { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; }
    .back-link { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: color-mix(in oklab, var(--chrome-text) 55%, transparent); text-decoration: none; }
    .back-link:hover { color: var(--chrome-text); }
    .board-title { font-family: 'Instrument Serif', serif; font-size: 1.4rem; font-weight: 400; color: var(--chrome-text); margin: 0; }
    .empty, .info { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: color-mix(in oklab, var(--chrome-text) 55%, transparent); }
</style>
