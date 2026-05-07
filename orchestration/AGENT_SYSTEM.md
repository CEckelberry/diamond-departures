# Diamond Departures — Agent System (Local-LLM First)

## Objective

Implement this project with **local LLM as primary coder** (llama-swap), while orchestrator agents handle planning, review, verification, and progress control.

## Coding model routing

- **Test authoring (RED phase):** `coder-accurate`
- **Implementation (GREEN phase):** `coder-fast`
- **Refactor/edge-case cleanup:** `coder-accurate`
- Long-context planner/reader: `planner-longctx`

Endpoint: `http://127.0.0.1:8080/v1`

## Agent roles

1. **Planner Agent**
   - Break TASKS.md into 1–3 hour packets
   - Define inputs/outputs/acceptance checks
2. **Local Coder Agent**
   - Uses local model to draft code/diffs for one packet at a time
3. **Reviewer Agent**
   - Checks output against packet acceptance criteria
4. **Verifier Agent**
   - Runs tests/lint/build and confirms done/not-done
5. **Git Sync Agent**
   - Every 2–3 completed packets: commit, pull --rebase, push
6. **Check-in Agent**
   - Writes status snapshots to `orchestration/checkins/`

## Cadence

- **Per packet (TDD):** plan -> tests first (RED) -> implement (GREEN) -> refactor -> review -> verify
- **Every 2 packets**: git sync checkpoint
- **Daily**: one high-level health check (scope drift, blockers, quality)

## Hard rules

- TDD is mandatory for all new packets: write failing tests first, then implement.
- Never start a new packet if current packet acceptance criteria are failing.
- One owner per file per packet (avoid overlap).
- Prefer sequential execution for same subsystem.
- Keep artifacts for every run in `orchestration/runs/`.
