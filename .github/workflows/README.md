# CI scaffold

`ci.yml` runs on every push and pull request.

## Jobs

- `changes`: detects touched app/workflow/test paths via `dorny/paths-filter`.
- `lint`: runs `actionlint` and Python syntax checks.
- `test`: runs Python unit tests.
- `build`: installs workspace deps and runs available build scripts.
- `deploy`: placeholder only, disabled until Phase 7.

## Secrets

No custom secrets required yet.
Future deploy stage will need cloud deploy credentials (TBD in Phase 7).
