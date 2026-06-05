<script lang="ts">
    import PremiumGate from '$lib/components/auth/PremiumGate.svelte';
    import SEO from '$lib/components/shell/SEO.svelte';

    let { data } = $props();
    let newName = $state('');
    let boards = $state<any[]>(data.boards ?? []);

    async function createBoard() {
        if (!newName.trim()) return;
        const resp = await fetch('/api/watch-boards', {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ name: newName.trim() }),
        });
        if (resp.ok) {
            boards = [await resp.json(), ...boards];
            newName = '';
        }
    }

    async function deleteBoard(id: string) {
        await fetch(`/api/watch-boards/${id}`, { method: 'DELETE' });
        boards = boards.filter((b) => b.id !== id);
    }
</script>

<SEO title="Watch Boards — Diamond Departures" description="Your custom player boards." path="/boards" />

<div class="boards-page">
    <PremiumGate feature="Watch Boards">
        <div class="boards-inner">
            <h1 class="page-title">Watch Boards</h1>
            <div class="create-row">
                <input
                    class="name-input"
                    bind:value={newName}
                    placeholder="New board name"
                    onkeydown={(e) => e.key === 'Enter' && createBoard()}
                />
                <button class="create-btn" onclick={createBoard}>Create</button>
            </div>
            {#if boards.length === 0}
                <p class="empty">No boards yet. Create one above.</p>
            {:else}
                <ul class="board-list">
                    {#each boards as board (board.id)}
                        <li class="board-item">
                            <a href="/boards/{board.id}" class="board-link">{board.name}</a>
                            <button class="delete-btn" onclick={() => deleteBoard(board.id)}>✕</button>
                        </li>
                    {/each}
                </ul>
            {/if}
        </div>
    </PremiumGate>
</div>

<style>
    .boards-page { padding: calc(var(--nav-height) + 2rem) 1rem 2rem; max-width: 640px; margin: 0 auto; }
    .page-title { font-family: 'Instrument Serif', serif; font-size: 1.5rem; font-weight: 400; color: var(--chrome-text); margin: 0 0 1.5rem; }
    .create-row { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; }
    .name-input {
        flex: 1;
        background: color-mix(in oklab, var(--chrome-bg) 80%, transparent);
        border: 1px solid color-mix(in oklab, var(--chrome-text) 18%, transparent);
        border-radius: 0.3rem;
        color: var(--chrome-text);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        padding: 0.4rem 0.75rem;
    }
    .create-btn {
        background: var(--mlb-red); color: #fff; border: none; border-radius: 0.3rem;
        font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 700;
        padding: 0.4rem 1rem; cursor: pointer;
    }
    .board-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.5rem; }
    .board-item {
        display: flex; align-items: center; justify-content: space-between;
        padding: 0.75rem 1rem;
        border: 1px solid color-mix(in oklab, var(--chrome-text) 10%, transparent);
        border-radius: 0.4rem;
    }
    .board-link { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: var(--chrome-text); text-decoration: none; }
    .board-link:hover { color: var(--mlb-red); }
    .delete-btn { background: none; border: none; color: color-mix(in oklab, var(--chrome-text) 35%, transparent); cursor: pointer; font-size: 0.75rem; padding: 0.2rem; }
    .delete-btn:hover { color: var(--mlb-red); }
    .empty { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: color-mix(in oklab, var(--chrome-text) 45%, transparent); }
</style>
