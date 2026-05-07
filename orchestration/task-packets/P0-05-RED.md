# Packet P0-05-RED — CI scaffold tests first (TDD)

## Goal

Write failing tests first for Task 0.5 CI scaffold.

## Inputs

- `TASKS.md` Task 0.5
- expected workflow path `.github/workflows/ci.yml`

## Scope (tests only)

Create tests that validate CI workflow scaffold contract:

- `.github/workflows/ci.yml` exists
- workflow triggers on push + pull_request
- workflow uses path filtering to detect changed apps
- workflow defines lint/test/build style jobs
- workflow includes workflow-lint step using actionlint

## Required outputs

- `tests/ci/test_workflow_scaffold.py`

## Constraints

- No workflow implementation in this RED packet.
- Tests must fail before GREEN work.

## Acceptance checks

- `python3 -m unittest tests/ci/test_workflow_scaffold.py`
- At least one failing assertion in RED phase
