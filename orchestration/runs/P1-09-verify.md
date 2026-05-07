# P1-09 verification (schema drift detection)

Date: 2026-05-07

## RED evidence
- Command: `.venv/bin/pytest apps/ingest/tests/test_drift.py -q`
- Result: import error for missing `drift` module.

## GREEN verification
1. `.venv/bin/pytest apps/ingest/tests/test_drift.py -q`
   - Result: PASS (3 passed)

## Notes
- JSON shape hash remains stable when only primitive values change.
- Detector emits WARN when schema signature changes.
- Detector emits ERROR when required key path is missing.
- Added migration `004_drift_signatures` to persist drift signatures.
