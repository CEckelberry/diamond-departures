# P0-03-RED run log

## Packet
- `orchestration/task-packets/P0-03-RED.md`

## Local model generation
- Command: `python3 scripts/local_llm_task.py --model coder-accurate --task-file orchestration/task-packets/P0-03-RED.md --out orchestration/runs/P0-03-RED-coder-accurate.txt`
- Output artifact: `orchestration/runs/P0-03-RED-coder-accurate.txt`
- Note: Generated diff was reviewed; tests were implemented manually to keep contracts concise and RED-focused.

## Test command (RED)
- Command: `python -m unittest discover -s tests`
- Exit code: `1`

### Output
```text
F/usr/lib/python3.14/tempfile.py:484: ResourceWarning: Implicitly cleaning up <HTTPError 404: 'File not found'>
  _warnings.warn(self.warn_message, ResourceWarning)
FFFF
======================================================================
FAIL: test_game_feed_contract (mlb_mock.test_contracts.MLBMockContractTests.test_game_feed_contract)
----------------------------------------------------------------------
AssertionError: request failed for http://localhost:8090/api/v1/schedule?date=today: HTTP Error 404: File not found

======================================================================
FAIL: test_people_stats_contract (mlb_mock.test_contracts.MLBMockContractTests.test_people_stats_contract)
----------------------------------------------------------------------
AssertionError: request failed for http://localhost:8090/api/v1/people/660271/stats?group=hitting%2Cpitching: HTTP Error 404: File not found

======================================================================
FAIL: test_replay_speed_contract (mlb_mock.test_contracts.MLBMockContractTests.test_replay_speed_contract)
----------------------------------------------------------------------
AssertionError: request failed for http://localhost:8090/api/v1/schedule?date=today: HTTP Error 404: File not found

======================================================================
FAIL: test_roster_contract (mlb_mock.test_contracts.MLBMockContractTests.test_roster_contract)
----------------------------------------------------------------------
AssertionError: request failed for http://localhost:8090/api/v1/teams/147/roster: HTTP Error 404: File not found

======================================================================
FAIL: test_schedule_today_contract (mlb_mock.test_contracts.MLBMockContractTests.test_schedule_today_contract)
----------------------------------------------------------------------
AssertionError: request failed for http://localhost:8090/api/v1/schedule?date=today: HTTP Error 404: File not found

----------------------------------------------------------------------
Ran 5 tests in 0.025s

FAILED (failures=5)
```

## GREEN packet notes
- Implement `apps/mlb-mock/app/main.py` with routes for all four endpoints.
- Ensure response JSON contains required keys asserted in `tests/mlb_mock/test_contracts.py`.
- `people/{id}/stats` must include both `hitting` and `pitching` stat groups when `group=hitting,pitching`.
- Replay mode must produce at least one live game in schedule and observable progression across repeated `feed/live` polls.
