# Packet P-LIVE-03 — Scanner delta payload GREEN

## Goal
Emit deterministic scanner delta payloads for downstream board refresh/SSE workflows.

## GREEN scope
- Add delta helper module for changed players + affected views.
- Wire helper into ingest job output.
- Verify output shape and values via tests.

## Acceptance
- New delta tests pass.
- Ingest suite remains green.
