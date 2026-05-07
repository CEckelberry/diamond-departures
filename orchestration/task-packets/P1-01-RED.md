# Packet P1-01-RED — hitting stats tests first (TDD)

## Goal

Start Task 1.1 with tests-first for hitting stat formulas.

## Inputs

- `STATS.md` hitting formulas
- package target: `packages/stats/hitting`

## Scope (tests only)

Create RED tests for base hitting formulas:

- AVG, OBP, SLG, OPS, ISO, BABIP
- include zero-denominator guard cases
- include one table of hand-verified sample values

## Required outputs

- `packages/stats/hitting/tests/test_basic.py`

## Constraints

- No implementation files in RED packet.
- Tests should fail before implementation exists.

## Acceptance checks

- `pytest packages/stats/hitting/tests/test_basic.py`
- RED state present
