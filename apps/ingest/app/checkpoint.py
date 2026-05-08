from __future__ import annotations

import json
from pathlib import Path


def _to_int(value: object, default: int = 0) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def load_checkpoint(path: str) -> dict[str, object]:
    target = Path(path)
    if not target.exists():
        return {
            "updated_since": None,
            "last_success_at": None,
            "consecutive_failures": 0,
            "scan_count": 0,
        }

    payload = json.loads(target.read_text(encoding="utf-8"))
    return {
        "updated_since": payload.get("updated_since"),
        "last_success_at": payload.get("last_success_at"),
        "consecutive_failures": _to_int(payload.get("consecutive_failures", 0), 0),
        "scan_count": _to_int(payload.get("scan_count", 0), 0),
    }


def save_checkpoint(path: str, payload: dict[str, object]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    normalized = {
        "updated_since": payload.get("updated_since"),
        "last_success_at": payload.get("last_success_at"),
        "consecutive_failures": _to_int(payload.get("consecutive_failures", 0), 0),
        "scan_count": _to_int(payload.get("scan_count", 0), 0),
    }

    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(json.dumps(normalized, indent=2) + "\n", encoding="utf-8")
    tmp.replace(target)
