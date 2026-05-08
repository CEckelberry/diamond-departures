# Packet P-LIVE-01-RED — Provider abstraction + game-change scanner tests first

## Goal

Define failing tests for a pluggable live-data provider and game-change driven scanner path using MLB Stats API semantics.

## RED scope

- Provider interface contract tests for schedule/live feed/game changes.
- Job behavior tests proving scanner mode uses `/api/v1/game/changes` then fetches only changed games.
- Config tests for provider selection env vars.

## Acceptance

- New tests fail before implementation.
