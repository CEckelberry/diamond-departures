# P-LIVE-03 verification (scanner delta payloads)

Date: 2026-05-08

## RED evidence

- Added tests:
  - `apps/ingest/tests/test_live_delta.py`
  - `apps/ingest/tests/test_job.py` delta payload assertions

## GREEN verification

- `.venv/bin/pytest apps/ingest/tests/test_live_delta.py apps/ingest/tests/test_job.py -q` → PASS
- `.venv/bin/pytest apps/ingest/tests -q` → PASS (36 passed)
- `node --test apps/web/tests/*.test.mjs` → PASS (73 passed)

## Implemented

- Added delta helper module: `apps/ingest/app/live_delta.py`
- Job now emits `delta_payload` in both success and degraded paths:
  - `changed_player_ids`
  - `affected_views`
- Added stable regex-flex test assertion for OG route quote style in `apps/web/tests/seo-og.test.mjs`.

## Local GPU run evidence

- Artifacts:
  - `orchestration/runs/P-LIVE-03-plan-longctx.txt`
  - `orchestration/runs/P-LIVE-03-RED-coder-accurate.txt`
- GPU trace: `orchestration/runs/P-LIVE-03-gpu-usage.csv` (card0 sustained around 95-97%).
