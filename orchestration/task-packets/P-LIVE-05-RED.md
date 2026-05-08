# Packet P-LIVE-05-RED — Continuous scanner loop + ops report tests first

## Goal
Create failing tests for a long-running scanner loop and durable run-report artifact.

## RED scope
- Config tests for live/idle scan intervals and scanner report path.
- Runner tests for:
  - dynamic sleep cadence (live vs idle)
  - persisted scanner report JSON after each iteration
  - carrying `snapshot` forward between iterations

## Acceptance
- New tests fail before implementation.
