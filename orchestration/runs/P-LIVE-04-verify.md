# P-LIVE-04 verification (reconciliation cadence + scanner telemetry)

Date: 2026-05-08

## RED evidence

- Added tests for reconciliation cadence and scan-count telemetry:
  - `apps/ingest/tests/test_config.py`
  - `apps/ingest/tests/test_checkpoint.py`
  - `apps/ingest/tests/test_job.py`

## GREEN verification

- `.venv/bin/pytest apps/ingest/tests/test_config.py apps/ingest/tests/test_checkpoint.py apps/ingest/tests/test_job.py apps/ingest/tests/test_provider.py apps/ingest/tests/test_live_delta.py -q` → PASS (14 passed)
- `.venv/bin/pytest apps/ingest/tests -q` → PASS (37 passed)
- `node --test apps/web/tests/*.test.mjs` → PASS (73 passed)

## Implemented

- Added `reconcile_every_n_scans` config (`RECONCILE_EVERY_N_SCANS`).
- Extended checkpoint payload with `scan_count` persistence.
- Job now increments `scan_count` per run and triggers full-live reconciliation sweep every N scans in changes mode.
- Added reconciliation telemetry fields in output:
  - `scanner_scan_count`
  - `reconcile_triggered`
  - `reconcile_games_count`

## Local GPU run evidence

- Artifacts:
  - `orchestration/runs/P-LIVE-04-plan-longctx.txt`
  - `orchestration/runs/P-LIVE-04-RED-coder-accurate.txt`
- GPU trace: `orchestration/runs/P-LIVE-04-gpu-usage.csv` with sustained card0 spikes around 92-95%.
