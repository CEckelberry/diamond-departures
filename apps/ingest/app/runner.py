from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .config import IngestSettings, load_settings
from .job import run_once
from .season_stats import SeasonStatsRefresher


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
    refresher = SeasonStatsRefresher(
        database_url=resolved.database_url,
        mlb_api_url=resolved.mlb_api_url,
    )
    previous_snapshot: set[str] | None = None
    last_season_refresh: datetime | None = None
    iteration = 0

    while True:
        result = run_once_fn(previous_snapshot=previous_snapshot)
        iteration += 1
        snapshot = result.get('snapshot')
        if isinstance(snapshot, set):
            previous_snapshot = snapshot

        has_live_games = bool(result.get('live_games'))
        refresh_interval = (
            resolved.season_refresh_live_seconds
            if has_live_games
            else resolved.season_refresh_idle_seconds
        )

        now = datetime.now(UTC)
        since_last = (now - last_season_refresh).total_seconds() if last_season_refresh else None
        if since_last is None or since_last >= refresh_interval:
            try:
                refresh_result = refresher.refresh(season=resolved.current_season)
                if refresh_result.errors:
                    import logging
                    logging.getLogger("apps.ingest.runner").warning(
                        "season refresh errors: %s", refresh_result.errors
                    )
            except Exception as exc:
                import logging
                logging.getLogger("apps.ingest.runner").error("season refresh failed: %s", exc)
            last_season_refresh = now

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

        sleep_seconds = (
            resolved.scan_interval_live_seconds
            if has_live_games
            else resolved.scan_interval_idle_seconds
        )
        sleep_fn(float(sleep_seconds))
