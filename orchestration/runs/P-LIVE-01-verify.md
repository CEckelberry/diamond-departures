# P-LIVE-01 verification (provider abstraction + game-change scanner)

Date: 2026-05-08

## RED evidence
- Added tests:
  - `apps/ingest/tests/test_provider.py`
  - `apps/ingest/tests/test_job.py` (scanner mode coverage)
  - `apps/ingest/tests/test_config.py` (provider/scanner envs)

## GREEN verification
- `.venv/bin/pytest apps/ingest/tests/test_config.py apps/ingest/tests/test_provider.py apps/ingest/tests/test_job.py -q` → PASS (7 passed)
- `.venv/bin/pytest apps/ingest/tests -q` → PASS (30 passed)

## Implemented
- Added provider abstraction and MLB stats implementation:
  - `apps/ingest/app/provider.py`
- Added settings for source/scanner mode + lookback window:
  - `apps/ingest/app/config.py`
- Added scanner behavior in job loop using game changes endpoint path:
  - `apps/ingest/app/job.py`
- Added changed-game extraction helper:
  - `apps/ingest/app/schedule.py`

## Local GPU run evidence
- Planner/test generation artifacts:
  - `orchestration/runs/P-LIVE-01-plan-longctx.txt`
  - `orchestration/runs/P-LIVE-01-RED-coder-accurate.txt`
- GPU utilization trace in `orchestration/runs/P-LIVE-01-gpu-usage.csv` with sustained spikes around 92-94% on card0.
