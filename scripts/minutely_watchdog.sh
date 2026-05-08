#!/usr/bin/env bash
set -euo pipefail

ROOT="/home/roger/Documents/coding/cole-portfolio-apps/diamond-departures"
cd "$ROOT"

LOG="orchestration/runs/minutely-watchdog.log"
QUEUE_FILE="orchestration/local-llm-queue-phase7b.csv"

mkdir -p orchestration/runs

echo "[$(date -Iseconds)] watchdog started" >>"$LOG"

while true; do
  ts="$(date -Iseconds)"
  gpu_line="$(rocm-smi -u --json 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(str(d.get('card0',{}).get('GPU use (%)','na')) + ',' + str(d.get('card1',{}).get('GPU use (%)','na')))" 2>/dev/null || echo 'na,na')"

  queue_pid="$(pgrep -af "run_local_llm_queue.py --queue-file ${QUEUE_FILE}" | awk 'NR==1{print $1}' || true)"
  task_line="$(pgrep -af "python3 scripts/local_llm_task.py" | head -n 1 | cut -c1-220 || true)"

  if [[ -z "${queue_pid:-}" ]]; then
    nohup python3 scripts/run_local_llm_queue.py --queue-file "$QUEUE_FILE" --continue-on-error >orchestration/runs/local-llm-queue-phase7b.log 2>&1 &
    new_pid="$!"
    echo "[$ts] gpu=${gpu_line} queue=RESTARTED pid=${new_pid} task='${task_line:-none}'" >>"$LOG"
  else
    echo "[$ts] gpu=${gpu_line} queue=RUNNING pid=${queue_pid} task='${task_line:-none}'" >>"$LOG"
  fi

  sleep 60
done
