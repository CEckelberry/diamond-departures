from __future__ import annotations

import json
from pathlib import Path

from ..harness import run_verification


def test_run_verification_passes_for_curated_dataset() -> None:
    assert run_verification() == []


def test_run_verification_surfaces_mismatch(tmp_path: Path) -> None:
    from ..harness import DEFAULT_DATA_PATH

    payload = json.loads(DEFAULT_DATA_PATH.read_text(encoding="utf-8"))
    payload["entries"][0]["expected"]["avg"] = 0.100001

    custom = tmp_path / "data.json"
    custom.write_text(json.dumps(payload), encoding="utf-8")

    mismatches = run_verification(path=custom)
    assert mismatches
    first = mismatches[0]
    assert first.player_id == payload["entries"][0]["player_id"]
    assert first.stat_key == "avg"
