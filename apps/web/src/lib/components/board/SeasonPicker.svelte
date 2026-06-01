<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';

    const CURRENT_YEAR = new Date().getFullYear();
    const YEARS = Array.from({ length: CURRENT_YEAR - 2016 + 1 }, (_, i) => CURRENT_YEAR - i);

    const activeSeason = $derived(
        parseInt($page.url.searchParams.get('season') ?? String(CURRENT_YEAR))
    );

    function chooseSeason(year: number) {
        const params = new URLSearchParams($page.url.searchParams);
        if (year === CURRENT_YEAR) {
            params.delete('season');
        } else {
            params.set('season', String(year));
        }
        const search = params.toString();
        void goto(search ? `${$page.url.pathname}?${search}` : $page.url.pathname, {
            replaceState: false,
            keepFocus: true,
            noScroll: true,
        });
    }
</script>

<div class="season-picker" role="listbox" aria-label="Season selector">
    {#each YEARS as year}
        <button
            role="option"
            aria-selected={year === activeSeason}
            class:active={year === activeSeason}
            onclick={() => chooseSeason(year)}
        >
            {year}
            {#if year === CURRENT_YEAR}
                <span class="live-dot" aria-label="Live season"></span>
            {/if}
        </button>
    {/each}
</div>

<style>
    .season-picker {
        display: flex;
        gap: 0.25rem;
        overflow-x: auto;
        scrollbar-width: none;
    }
    .season-picker::-webkit-scrollbar { display: none; }

    button {
        flex: none;
        display: flex;
        align-items: center;
        gap: 0.3rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.04em;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        border: 1px solid color-mix(in oklab, var(--chrome-text) 18%, transparent);
        background: color-mix(in oklab, var(--chrome-bg) 60%, black);
        color: color-mix(in oklab, var(--chrome-text) 60%, transparent);
        cursor: pointer;
    }

    button.active {
        background: var(--mlb-blue);
        border-color: var(--mlb-blue);
        color: white;
    }

    .live-dot {
        display: inline-block;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #22c55e;
        animation: pulse 1.8s ease-in-out infinite;
        flex-shrink: 0;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%       { opacity: 0.5; transform: scale(0.8); }
    }
</style>
