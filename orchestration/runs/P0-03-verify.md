# P0-03 verification (GREEN)

Date: 2026-05-07
Scope: execute tests in `tests/mlb_mock`, handle port `8090` conflict safely, record exact commands and outcomes.

## Commands + outcomes

1. Check if `8090` occupied

- Command:
  ```bash
  docker ps --filter publish=8090 --format '{{.ID}} {{.Names}} {{.Ports}}'
  ```
- Output:
  ```text
  b5544a7b8195 backend-bakeoff-router-1 0.0.0.0:8090->8080/tcp, [::]:8090->8080/tcp
  ```
- Outcome: conflict found (`backend-bakeoff-router-1`).

2. Temporarily stop conflicting service (safe: Docker container with known ID/name, restart command available)

- Command:
  ```bash
  docker stop b5544a7b8195
  ```
- Output:
  ```text
  b5544a7b8195
  ```
- Outcome: stopped.

3. Start MLB mock service for tests

- Command:
  ```bash
  python3 apps/mlb-mock/app/main.py --replay-speed 300 >/tmp/mlb-mock-verify.log 2>&1 & echo $!
  ```
- Output:
  ```text
  3316289
  ```
- Outcome: mock started as PID `3316289`.

4. Confirm listener on `8090`

- Command:
  ```bash
  sleep 1; ss -ltnp '( sport = :8090 )'
  ```
- Output:
  ```text
  State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
  LISTEN 0      5            0.0.0.0:8090      0.0.0.0:*    users:(("python3",pid=3316289,fd=3))
  ```
- Outcome: correct process bound.

5. Run contract tests

- Command:
  ```bash
  python3 -m unittest tests/mlb_mock/test_contracts.py
  ```
- Output:

  ```text
  .....
  ----------------------------------------------------------------------
  Ran 5 tests in 1.012s

  OK
  ```

- Outcome: PASS.

6. Run discovery scoped to `tests/mlb_mock`

- Command:
  ```bash
  python3 -m unittest discover -s tests/mlb_mock
  ```
- Output:

  ```text
  .....
  ----------------------------------------------------------------------
  Ran 5 tests in 1.012s

  OK
  ```

- Outcome: PASS.

7. Stop temporary mock process

- Command:
  ```bash
  kill 3316289 && sleep 1; ps -p 3316289 -o pid=,stat=,cmd= || true
  ```
- Output:
  ```text
  (no output)
  ```
- Outcome: mock process terminated.

8. Restart previously stopped service

- Command:
  ```bash
  docker start b5544a7b8195
  ```
- Output:
  ```text
  b5544a7b8195
  ```
- Outcome: original service restored.

9. Final port check

- Command:
  ```bash
  ss -ltnp '( sport = :8090 )'
  ```
- Output:
  ```text
  State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
  LISTEN 0      4096         0.0.0.0:8090      0.0.0.0:*    users:(("rootlesskit",pid=787056,fd=127))
  LISTEN 0      4096            [::]:8090         [::]:*    users:(("rootlesskit",pid=787056,fd=128))
  ```
- Outcome: `8090` back to Docker/rootlesskit listener.

## Verification result

- Packet status: **GREEN confirmed** for `tests/mlb_mock`.
- Failing checks: **none**.
- Next action: mark P0-03 verify complete on task board/check-in flow.
