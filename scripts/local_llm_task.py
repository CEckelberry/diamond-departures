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
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--top-p", type=float, default=None)
    parser.add_argument("--max-tokens", type=int, default=None)
    parser.add_argument(
        "--profile",
        choices=["impl", "test", "plan"],
        default="impl",
        help="Preset sampling profile when explicit sampling args are omitted.",
    )
    args = parser.parse_args()

    task_text = pathlib.Path(args.task_file).read_text(encoding="utf-8")

    profile_defaults = {
        "impl": {"temperature": 0.22, "top_p": 0.92, "max_tokens": 9000},
        "test": {"temperature": 0.30, "top_p": 0.94, "max_tokens": 11000},
        "plan": {"temperature": 0.28, "top_p": 0.93, "max_tokens": 14000},
    }
    chosen = profile_defaults[args.profile]
    temperature = args.temperature if args.temperature is not None else chosen["temperature"]
    top_p = args.top_p if args.top_p is not None else chosen["top_p"]
    max_tokens = args.max_tokens if args.max_tokens is not None else chosen["max_tokens"]

    payload = {
        "model": args.model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a senior engineer. Produce implementation-ready output for exactly one task packet. "
                    "Think deeply and be explicit about edge cases and failure modes. "
                    "Return: (1) plan with assumptions+risks, (2) exact file edits as unified diff, (3) verification commands."
                ),
            },
            {"role": "user", "content": task_text},
        ],
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
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
