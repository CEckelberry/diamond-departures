# P1-01 verification (hitting package start)

Date: 2026-05-07

## Assumptions
- "Start P1-01" interpreted as implementing the first formula slice (basic hitting stats) with tests-first.
- Full Task 1.1 scope (wOBA/wRC+/weights/context/coverage target) remains open.

## RED -> GREEN evidence
- RED: `.venv/bin/pytest packages/stats/hitting/tests/test_basic.py -q` failed with module import error (no hitting package implementation).
- GREEN: same command passes after creating package + `basic.py` functions.

## Verification commands + outcomes
1. `.venv/bin/pytest packages/stats/hitting/tests/test_basic.py -q` -> PASS (7 passed)
2. `python3 -m unittest tests/devstack/test_compose_acceptance.py tests/ci/test_workflow_scaffold.py tests/web/test_web_bootstrap.py` -> PASS

## Result
- P1-01 started and currently in progress; base formulas implemented (AVG/OBP/SLG/OPS/ISO/BABIP).
