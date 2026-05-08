# Packet P-LIVE-05 — Continuous scanner loop + ops report GREEN

## Goal
Enable continuous scanner operation with reliable reporting for operations visibility.

## GREEN scope
- Add scanner loop runner module.
- Add env-configurable live/idle loop cadence.
- Write scanner run report JSON each iteration.

## Acceptance
- New runner/config tests pass.
- Ingest suite remains green.
