# Packet P-LIVE-02 — Scanner checkpoint/cursor reliability GREEN

## Goal
Implement durable scanner cursor + reliability metrics for game-change polling.

## GREEN scope
- Add checkpoint store module with JSON persistence.
- Wire checkpoint read/write into ingest job scanner mode.
- Add failure accounting and lag/changed-game/feed-failure metrics in run output.

## Acceptance
- New checkpoint/reliability tests pass.
- Existing ingest suite remains green.
