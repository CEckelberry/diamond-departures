# Packet P1-09-RED — schema drift detection tests first

## Goal

Task 1.9 RED: verify schema shape hash stability and drift/error signaling.

## Scope

Create failing tests for:

1. stable shape hash across equivalent payload values.
2. WARN-level drift record when new schema key appears.
3. ERROR-level record when required key path disappears.

## Constraints

- RED only.
- No external services.
- Hashing must ignore value changes and focus on shape.

## Acceptance

`.venv/bin/pytest apps/ingest/tests/test_drift.py -q`
