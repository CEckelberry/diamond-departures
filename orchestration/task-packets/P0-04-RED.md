# Packet P0-04-RED — local dev compose acceptance tests first (TDD)

## Goal

Write failing tests first for Task 0.4 local dev compose acceptance.

## Required context

- `TASKS.md` Task 0.4
- `docker-compose.yml`
- `Makefile`

## Scope (tests only)

Add automated tests that validate:

- Compose services include: `db`, `db-init`, `mlb-mock`, `api`, `ingest`, `web`
- Host ports map to acceptance values: db `5432`, mlb-mock `8090`, web `5173`
- `db` image is `postgres:18-alpine`
- `make dev` and `make dev-clean` targets exist

## Required outputs

- `tests/devstack/test_compose_acceptance.py`

## Constraints

- No production file edits in this packet.
- RED state required: tests must fail against current config before GREEN changes.

## Acceptance checks

- `python3 -m unittest tests/devstack/test_compose_acceptance.py` runs
- At least one assertion fails before GREEN implementation

## Deliver back

1. Unified diff
2. RED test output
3. Notes for GREEN implementation
