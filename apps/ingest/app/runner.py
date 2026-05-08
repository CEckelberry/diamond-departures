from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .config import IngestSettings, load_settings
from .job import run_once


def _iso_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _write_report(path: str, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + '.tmp')
    tmp.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    tmp.replace(target)


def run_loop(
    *,
    max_iterations: int | None = None,
    settings: IngestSettings | None = None,
    run_once_fn: Callable[..., dict[str, Any]] = run_once,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> None:
    resolved = settings or load_settings()
    previous_snapshot: set[str] | None = None
    iteration = 0

    while True:
        result = run_once_fn(previous_snapshot=previous_snapshot)
        iteration += 1
        snapshot = result.get('snapshot')
        if isinstance(snapshot, set):
            previous_snapshot = snapshot

        report = {
            'iteration': iteration,
            'written_at': _iso_now(),
            'status': result.get('status'),
            'scanner_mode': result.get('scanner_mode'),
            'live_games_count': len(result.get('live_games', [])),
            'changed_games_count': result.get('changed_games_count', 0),
            'event_count': result.get('event_count', 0),
            'update_count': result.get('update_count', 0),
            'scanner_scan_count': result.get('scanner_scan_count', 0),
            'reconcile_triggered': bool(result.get('reconcile_triggered', False)),
            'reconcile_games_count': result.get('reconcile_games_count', 0),
            'error': result.get('error'),
        }
        _write_report(resolved.scanner_report_path, report)

        if max_iterations is not None and iteration >= max_iterations:
            return

        has_live_games = bool(result.get('live_games'))
        sleep_seconds = (
            resolved.scan_interval_live_seconds
            if has_live_games
            else resolved.scan_interval_idle_seconds
        )
        sleep_fn(float(sleep_seconds))
