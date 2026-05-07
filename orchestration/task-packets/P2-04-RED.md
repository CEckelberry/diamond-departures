# Packet P2-04-RED — Pub/Sub subscriber invalidation flow tests first

## Goal

Task 2.4 RED start: define failing tests for ingest notification subscriber and cache invalidation wiring.

## Scope

Create failing tests for:

1. Subscriber parses refresh message and invalidates each targeted `(view, sort)` key.
2. Subscriber ACKs message after successful invalidation.
3. Subscriber NACKs message when invalidation raises.
4. Subscriber logs refreshed keys with reason for observability.

## Constraints

- RED-only start.
- No real cloud Pub/Sub dependency in unit tests.

## Acceptance

`.venv/bin/pytest apps/api/tests/test_pubsub.py -q`
