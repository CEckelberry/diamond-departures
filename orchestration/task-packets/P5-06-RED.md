# Packet P5-06-RED — Freshness debug panel tests first

## Goal
Create failing tests for full freshness debug panel component + header wiring.

## RED scope
- Add tests asserting:
  - `FreshnessPanel.svelte` exists and fetches `/api/freshness`
  - panel includes ingest runs list, per-stat freshness section, schema drift section
  - panel is accessible (`role="dialog"`, close button, aria labels)
  - Header imports/renders `FreshnessPanel` instead of placeholder text panel

## Acceptance
- Tests fail before implementation.
