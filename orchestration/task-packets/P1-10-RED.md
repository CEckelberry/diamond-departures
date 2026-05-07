# Packet P1-10-RED — position taxonomy + qualification tests first

## Goal

Task 1.10 RED: define failing tests for position classification, eligibility, and qualification transitions.

## Scope

Create failing tests for:

1. Non-pitcher primary position and eligibility (`2B` primary, `2B/SS` eligible).
2. Tie and multi-position handling (`LF/RF` tie => `OF`; 3+ positions => `UT`).
3. Pitcher role split (`SP` when starts ratio > 0.5; else `RP`).
4. Qualification thresholds for hitter/SP/RP and `just_qualified_at` transition timestamp behavior.

## Constraints

- RED only.
- No DB/network calls.
- Rules sourced from `DATA.md` and `STATS.md`.

## Acceptance

`.venv/bin/pytest apps/ingest/tests/test_positions.py -q`
