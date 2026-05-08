# Packet P-LIVE-04-RED — Reconciliation cadence + scanner telemetry tests first

## Goal
Create failing tests for periodic full-live reconciliation sweeps and scan-count telemetry.

## RED scope
- Config coverage for reconciliation cadence env var.
- Checkpoint coverage for persisted `scan_count`.
- Job behavior: in changes mode, every Nth scan triggers full live reconciliation.
- Job output includes reconciliation telemetry fields.

## Acceptance
- New tests fail before implementation.
