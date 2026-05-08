# Packet P-LIVE-03-RED — Scanner delta payload tests first

## Goal
Create failing tests for scanner-produced downstream delta payloads (changed players + affected board views).

## RED scope
- Derive changed player IDs from updates.
- Derive affected board views/sorts using leaderboard mapping helpers.
- Ensure run output includes machine-friendly delta payload fields.

## Acceptance
- New tests fail before implementation.
