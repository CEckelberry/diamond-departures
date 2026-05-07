# P0-04 verification (local dev compose)

Date: 2026-05-07

## Assumptions
- Host ports mandated by Task 0.4 are authoritative: db `5432`, mlb-mock `8090`, web `5173`.
- Existing local services on those ports can be temporarily stopped for validation, then restored.

## RED -> GREEN evidence
- RED: `python3 -m unittest tests/devstack/test_compose_acceptance.py -v` failed on db/web host ports.
- GREEN: same test passed after compose + Makefile updates.

## Verification commands + outcomes
1. `docker compose config` -> PASS
2. `make dev` -> PASS (db, mlb-mock, api placeholder, ingest placeholder, web placeholder up; migrations applied by db-init)
3. `ss -ltn '( sport = :5432 or sport = :8090 or sport = :5173 )'` -> PASS (all listening)
4. `make dev-clean` -> PASS (containers, network, volume removed)

## Result
- Packet P0-04 accepted.
