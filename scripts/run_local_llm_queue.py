#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import subprocess
import time
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[1]


def gpu_use() -> tuple[str, str]:
    cmd = ["rocm-smi", "-u", "--json"]
    try:
        raw = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, cwd=ROOT)
        data = json.loads(raw.decode("utf-8"))
        c0 = str(data.get("card0", {}).get("GPU use (%)", "na"))
        c1 = str(data.get("card1", {}).get("GPU use (%)", "na"))
        return c0, c1
    except Exception:
        return "na", "na"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-file", required=True)
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    parser.add_argument("--continue-on-error", action="store_true")
    args = parser.parse_args()

    queue_path = pathlib.Path(args.queue_file)
    if not queue_path.is_absolute():
        queue_path = ROOT / queue_path

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = ROOT / "orchestration" / "runs" / f"queue-{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    gpu_csv = run_dir / "gpu-usage.csv"
    gpu_csv.write_text("timestamp,task_name,gpu_use_card0,gpu_use_card1\n", encoding="utf-8")

    with queue_path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    for i, row in enumerate(rows, start=1):
        name = row["name"].strip()
        cmd = [
            "python3",
            "scripts/local_llm_task.py",
            "--model",
            row["model"].strip(),
            "--profile",
            row["profile"].strip(),
            "--max-tokens",
            row.get("max_tokens", "22000").strip() or "22000",
            "--timeout",
            row.get("timeout", "2400").strip() or "2400",
            "--task-file",
            row["task_file"].strip(),
            "--out",
            row["out"].strip(),
        ]
        log_path = run_dir / f"{i:02d}-{name}.log"
        with log_path.open("w", encoding="utf-8") as logf:
            proc = subprocess.Popen(cmd, cwd=ROOT, stdout=logf, stderr=logf)
            while proc.poll() is None:
                c0, c1 = gpu_use()
                ts = datetime.now().isoformat(timespec="seconds")
                with gpu_csv.open("a", encoding="utf-8") as gf:
                    gf.write(f"{ts},{name},{c0},{c1}\n")
                time.sleep(args.poll_seconds)

            rc = proc.returncode or 0
            ts = datetime.now().isoformat(timespec="seconds")
            c0, c1 = gpu_use()
            with gpu_csv.open("a", encoding="utf-8") as gf:
                gf.write(f"{ts},{name},{c0},{c1}\n")

            status_path = run_dir / "status.json"
            status = {
                "last_task": name,
                "index": i,
                "total": len(rows),
                "returncode": rc,
                "updated_at": ts,
            }
            status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")

            if rc != 0 and not args.continue_on_error:
                raise SystemExit(rc)

    done = {
        "done": True,
        "total": len(rows),
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }
    (run_dir / "status.json").write_text(json.dumps(done, indent=2), encoding="utf-8")
    print(run_dir)


if __name__ == "__main__":
    main()
