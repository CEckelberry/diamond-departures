#!/usr/bin/env python3
"""Run one implementation packet against local llama-swap and save output artifacts."""

from __future__ import annotations

import argparse
import json
import pathlib
import urllib.request


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8080/v1")
    parser.add_argument("--model", default="coder-fast")
    parser.add_argument("--task-file", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()

    task_text = pathlib.Path(args.task_file).read_text(encoding="utf-8")
    payload = {
        "model": args.model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a senior engineer. Produce implementation-ready output for exactly one task packet. "
                    "Return: (1) concise plan, (2) exact file edits as unified diff, (3) verification commands."
                ),
            },
            {"role": "user", "content": task_text},
        ],
        "temperature": 0.15,
        "top_p": 0.9,
        "max_tokens": 3000,
        "stream": False,
    }

    req = urllib.request.Request(
        f"{args.base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=args.timeout) as response:
        body = json.loads(response.read().decode("utf-8"))

    content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
