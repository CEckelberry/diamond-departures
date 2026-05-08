# Packet P5-05-RED — Just-qualified animation tests first

## Goal

Capture failing tests for newly qualified row enter animation + badge fade contract.

## RED scope

- Add/extend web tests to assert:
  - board delta/store contract includes `newly_qualified` and `qualified_at`
  - row UI includes `(just qualified)` badge rendering path
  - enter animation hook/class exists for newly-qualified rows (800ms contract)
  - badge fade class references 24h animation variable (testable as shorter in CSS var)

## Acceptance

- Tests fail before implementation.
