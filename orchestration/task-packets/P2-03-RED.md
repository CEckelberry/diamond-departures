# Packet P2-03-RED — in-memory cache tests first

## Goal

Task 2.3 RED start: define failing tests for thread-safe leaderboard cache.

## Scope

Create failing tests for:

1. Cache loads rows for all keys on startup callback.
2. Cache reads return stored snapshots without mutation.
3. Cache invalidate refreshes one key from loader.

## Constraints

- RED-only start if time remains.
- No network/DB calls.

## Acceptance

`.venv/bin/pytest apps/api/tests/test_cache.py -q`
