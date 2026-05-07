# P1-03 verification (defensive parsers + qualification)

Date: 2026-05-07

## RED evidence
- Command: `.venv/bin/pytest packages/stats/defensive/tests -q`
- Result: module import failures for missing `parsers` and `qualification` before GREEN.

## GREEN verification
1. `.venv/bin/pytest packages/stats/defensive/tests -q`
   - Result: PASS (4 passed)
2. `.venv/bin/pytest packages/stats/hitting/tests packages/stats/pitching/tests packages/stats/defensive/tests -q`
   - Result: PASS (30 passed) for combined stats packages.

## Reviewer-style self-check
- Parsing coverage: DRS/UZR/UZR150/OAA extracted from representative MLB + Statcast payloads.
- Normalization: per-game UZR converted to UZR/150 (`uzr * 150`) when flagged.
- Qualification rule: `< 1000.0` innings returns `"noisy"`; threshold and above returns `None`.
- Risk note: parser currently targets known fixture shapes; additional upstream variants will need follow-up fixtures.
