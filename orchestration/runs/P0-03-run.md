# P0-03 run log

## Packet
- `orchestration/task-packets/P0-03.md`

## Local model generation
- Command: `python3 scripts/local_llm_task.py --model coder-fast --task-file orchestration/task-packets/P0-03.md --out orchestration/runs/P0-03-coder-fast.txt`
- Output artifact: `orchestration/runs/P0-03-coder-fast.txt`
- Review note: coder-fast draft did not match required endpoint paths/contract shape; implementation corrected manually to match `tests/mlb_mock/test_contracts.py`.
- Fallback note: `coder-accurate` not required.

## Files created
- `apps/mlb-mock/app/main.py`
- `apps/mlb-mock/app/data/schedule_today.json`
- `apps/mlb-mock/app/data/game_feed_template.json`
- `apps/mlb-mock/app/data/people_stats_660271.json`
- `apps/mlb-mock/app/data/roster_147.json`
- `apps/mlb-mock/Dockerfile`

## Validation commands
1. Contract tests only
   - Command:
     - `python3 apps/mlb-mock/app/main.py --replay-speed 300 >/tmp/mlb-mock.log 2>&1 &`
     - `python3 -m unittest tests/mlb_mock/test_contracts.py`
   - Result: PASS (`Ran 5 tests ... OK`)

2. Full test discovery
   - Command:
     - `python3 apps/mlb-mock/app/main.py --replay-speed 300 >/tmp/mlb-mock.log 2>&1 &`
     - `python3 -m unittest discover -s tests`
   - Result: PASS (`Ran 5 tests ... OK`)

## Notes
- Environment already had another service bound to `:8090` (`backend-bakeoff-router-1`) returning HTTP 404s.
- For validation, container was temporarily stopped, tests run against new mock service, then container restarted.
- Replay progression implemented via dynamic markers in `/api/v1/game/{id}/feed/live`:
  - `metaData.timeStamp`
  - `liveData.linescore.currentInning`
  - `liveData.linescore.inningState`
  - `liveData.plays.currentPlay.atBatIndex`
