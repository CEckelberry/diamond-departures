# Packet P6-02-RED — Preview mode replay tests first

## Goal

Create failing tests for off-season preview replay mode wiring.

## RED scope

- Add tests asserting:
  - off-season header includes Preview mode start/exit controls
  - frontend includes preview stream path `/api/board/preview-sse`
  - page tracks preview running state and clearly labels replay mode

## Acceptance

- `node --test apps/web/tests/preview-mode.test.mjs` fails before implementation.
