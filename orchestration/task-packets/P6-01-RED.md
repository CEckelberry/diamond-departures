# Packet P6-01-RED — Off-season banner/state tests first

## Goal
Create failing tests for off-season header presentation and SSE suppression behavior.

## RED scope
- Add web tests asserting:
  - Header shows off-season banner copy and countdown hook when mode is `off-season`
  - Board page skips `openBoardStream(...)` when off-season mode is active
  - Stat picker interactions still run in off-season state path

## Acceptance
- New packet tests fail before implementation.
