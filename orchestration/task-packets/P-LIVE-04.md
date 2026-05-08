# Packet P-LIVE-04 — Reconciliation cadence + scanner telemetry GREEN

## Goal
Improve scanner reliability by adding periodic full live sweeps to catch drift and expose explicit reconciliation telemetry.

## GREEN scope
- Add `RECONCILE_EVERY_N_SCANS` config.
- Persist `scan_count` in checkpoint.
- Trigger full-live reconciliation sweep every N scans in changes mode.
- Emit telemetry fields in job output (`scanner_scan_count`, `reconcile_triggered`, `reconcile_games_count`).

## Acceptance
- New reconciliation/telemetry tests pass.
- Ingest suite remains green.
