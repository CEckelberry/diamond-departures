<script lang="ts">
  import { einkStore } from '$lib/stores/eink';
  import type { EinkMode } from '$lib/stores/eink';

  const LABELS: Record<EinkMode, string> = {
    off: '🖥',
    aesthetic: '📄',
    faithful: '🖫',
  };

  const ARIA: Record<EinkMode, string> = {
    off: 'Enable e-ink aesthetic mode',
    aesthetic: 'Enable faithful e-ink mode',
    faithful: 'Disable e-ink mode',
  };
</script>

<button
  class="icon-btn"
  class:eink-active={$einkStore !== 'off'}
  type="button"
  aria-label={ARIA[$einkStore]}
  onclick={() => einkStore.cycle()}
>
  {LABELS[$einkStore]}
  {#if $einkStore !== 'off'}
    <span class="eink-label">{$einkStore === 'aesthetic' ? 'PAPER' : 'E-INK'}</span>
  {/if}
</button>

<style>
  .eink-active {
    border-color: color-mix(in oklab, var(--chrome-text) 50%, transparent);
  }

  .eink-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-left: 0.2rem;
  }
</style>
