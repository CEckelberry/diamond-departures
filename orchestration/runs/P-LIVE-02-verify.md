# P-LIVE-02 verification (scanner checkpoint + reliability metrics)

Date: 2026-05-08

## RED evidence
- Added tests:
  - `apps/ingest/tests/test_checkpoint.py`
  - `apps/ingest/tests/test_job.py` (checkpoint cursor + failure accounting)
  - `apps/ingest/tests/test_config.py` (checkpoint path env)

## GREEN verification
- `.venv/bin/pytest apps/ingest/tests/test_checkpoint.py apps/ingest/tests/test_job.py apps/ingest/tests/test_config.py apps/ingest/tests/test_provider.py -q` → PASS (11 passed)
- `.venv/bin/pytest apps/ingest/tests -q` → PASS (34 passed)
- `node --test apps/web/tests/seo-og.test.mjs` → PASS (3 passed)

## Implemented
- New durable checkpoint module: `apps/ingest/app/checkpoint.py`
- Added config setting `scanner_checkpoint_path` with env `SCANNER_CHECKPOINT_PATH`.
- Scanner job now:
  - loads/saves `updated_since` cursor
  - reuses checkpoint cursor when explicit override is absent
  - increments `consecutive_failures` when `/game/changes` fails
  - preserves prior cursor on changes failure
  - emits reliability metrics in run output (`scanner_lag_seconds`, `changed_games_count`, `feed_failures_count`)

## Local GPU run evidence
- Artifacts:
  - `orchestration/runs/P-LIVE-02-plan-longctx.txt`
  - `orchestration/runs/P-LIVE-02-RED-coder-accurate.txt`
- GPU trace: `orchestration/runs/P-LIVE-02-gpu-usage.csv` with sustained card0 spikes around 92-95%.
