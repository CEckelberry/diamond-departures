# Packet P-LIVE-01 — Provider abstraction + game-change scanner GREEN

## Goal
Implement a production-ready provider abstraction and first scanner mode for live MLB updates.

## GREEN scope
- Add provider abstraction and MLBStats provider implementation.
- Add game-change scanner path in ingest job.
- Add provider/config wiring for env-driven source selection.

## Acceptance
- New scanner/provider tests pass.
- Existing ingest tests remain green.
