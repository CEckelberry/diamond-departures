# P6-02 verification (preview mode replay frontend)

Date: 2026-05-08

## RED evidence
- Command: `node --test apps/web/tests/preview-mode.test.mjs`
- Result: FAIL before implementation (no preview controls, no preview mode state, no `/api/board/preview-sse` wiring).

## GREEN verification
1. `node --test apps/web/tests/preview-mode.test.mjs`
   - Result: PASS (3 passed)
2. `node --test apps/web/tests/*.test.mjs`
   - Result: PASS (54 passed)
3. `pnpm --filter web check`
   - Result: PASS (warnings only, no errors)

## Implementation notes
- Header now supports off-season Preview mode controls (`Preview mode` / `Exit preview mode`) and `Preview running` status pill.
- Board page now tracks `previewMode` state and shows `preview running · Replay mode` label.
- SSE client now supports endpoint override; board page uses `/api/board/preview-sse` when preview mode is enabled.
