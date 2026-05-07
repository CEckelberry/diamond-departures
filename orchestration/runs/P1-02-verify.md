# P1-02 verification (pitching package)

Date: 2026-05-07

## RED evidence
- Command: `.venv/bin/pytest packages/stats/pitching/tests -q`
- Result: module import failures for missing `basic`, `fip`, `siera`, `era_plus` before GREEN.

## GREEN verification
1. `.venv/bin/pytest packages/stats/pitching/tests -q`
   - Result: PASS (11 passed)
2. `.venv/bin/pytest packages/stats/hitting/tests packages/stats/pitching/tests -q`
   - Result: PASS (26 passed) to confirm no regressions in hitting package.

## Reviewer-style self-check
- Constants: `cfip_2026.json` added with `c_fip` and `league_hr_per_fb`; loader validates expected keys.
- Formula checks: ERA/WHIP/K9/BB9/K-BB%, FIP, xFIP, SIERA, ERA+ all verified with hand-computed fixtures.
- Guard behavior: zero-denominator paths return 0.0 consistently across all pitching functions.
- Risk note: SIERA uses deterministic coefficient form tied to implemented fixture; may differ from alternate public variants.
