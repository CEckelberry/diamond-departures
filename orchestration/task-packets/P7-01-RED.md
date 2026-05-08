# Packet P7-01-RED — Performance pass tests first

## Goal

Create failing tests/checks for frontend performance constraints.

## RED scope

- Add perf-contract tests for:
  - no unnecessary re-stream reconnects on sort/view toggles
  - lightweight board render path (no full re-seed for pure delta)
  - animation hooks respect reduced-motion path
- Add a quick benchmark/check script target for reproducible perf smoke checks.

## Acceptance

- New P7-01 checks fail before implementation.
