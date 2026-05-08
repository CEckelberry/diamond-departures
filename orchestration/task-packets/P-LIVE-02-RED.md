# Packet P-LIVE-02-RED — Scanner checkpoint/cursor reliability tests first

## Goal

Create failing tests for persistent `updatedSince` cursor state, failure accounting, and scan metrics.

## RED scope

- Checkpoint load/save behavior (file missing, valid JSON, atomic overwrite).
- Job behavior uses checkpoint cursor when `updated_since` is not provided.
- Job behavior updates checkpoint after successful changes scan.
- Job behavior increments failure count and preserves prior cursor when changes fetch fails.
- Scan metrics include lag and changed-game/feed failure counters.

## Acceptance

- New tests fail before implementation.
