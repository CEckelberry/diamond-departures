# Packet P6-03-RED — Between-games and no-games-today tests first

## Goal

Create failing tests for in-season idle states.

## RED scope

- Header copy contract for between-games and no-games-today states.
- SSE behavior contract:
  - still opens when not off-season
  - slower heartbeat/reconnect path in idle states
- Keep stat picker sorting active.

## Acceptance

- New packet tests fail before implementation.
