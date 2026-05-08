# P-LIVE-05 verification (continuous scanner loop + ops report)

Date: 2026-05-08

## RED evidence
- Added tests for scanner loop and ops reporting:
  - `apps/ingest/tests/test_runner.py`
  - `apps/ingest/tests/test_config.py` (new cadence/report envs)

## GREEN verification
- `.venv/bin/pytest apps/ingest/tests/test_config.py apps/ingest/tests/test_checkpoint.py apps/ingest/tests/test_job.py apps/ingest/tests/test_runner.py apps/ingest/tests/test_provider.py apps/ingest/tests/test_live_delta.py -q` → PASS (16 passed)
- `.venv/bin/pytest apps/ingest/tests -q` → PASS (39 passed)
- `node --test apps/web/tests/*.test.mjs` → PASS (73 passed)

## Implemented
- Added scanner runner: `apps/ingest/app/runner.py`
  - loops continuously with snapshot carry-forward
  - uses live/idle interval cadence from config
  - writes atomic scanner report JSON each iteration
- Added config fields:
  - `scan_interval_live_seconds` (`SCAN_INTERVAL_LIVE_SECONDS`)
  - `scan_interval_idle_seconds` (`SCAN_INTERVAL_IDLE_SECONDS`)
  - `scanner_report_path` (`SCANNER_REPORT_PATH`)

## Local GPU run evidence
- Artifacts:
  - `orchestration/runs/P-LIVE-05-plan-longctx.txt`
  - `orchestration/runs/P-LIVE-05-RED-coder-accurate.txt`
- GPU trace: `orchestration/runs/P-LIVE-05-gpu-usage.csv` with sustained card0 spikes in the high-90% band.
