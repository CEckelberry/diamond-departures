from __future__ import annotations

from datetime import UTC, datetime, timedelta

from .checkpoint import load_checkpoint, save_checkpoint
from .config import load_settings
from .game_processor import extract_stat_change_events
from .provider import build_provider
from .live_delta import build_delta_payload
from .schedule import extract_changed_game_ids, extract_live_game_ids
from .state_diff import diff_player_updates
from .store import init_store


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _format_utc(value: datetime) -> str:
    return value.replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _default_updated_since(lookback_seconds: int) -> str:
    point = _utc_now() - timedelta(seconds=lookback_seconds)
    return _format_utc(point)


def _safe_int(value: object, default: int = 0) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default


def _lag_seconds(updated_since: str | None) -> int | None:
    if not updated_since:
        return None
    try:
        parsed = datetime.fromisoformat(updated_since.replace('Z', '+00:00'))
    except ValueError:
        return None
    delta = _utc_now() - parsed
    return max(0, int(delta.total_seconds()))


def run_once(
    previous_snapshot: set[str] | None = None,
    updated_since: str | None = None,
) -> dict[str, object]:
    settings = load_settings()
    provider = build_provider(settings)
    store = init_store(settings.database_url)
    schedule = provider.fetch_schedule()

    checkpoint = load_checkpoint(settings.scanner_checkpoint_path)

    live_game_ids = extract_live_game_ids(schedule.payload)
    games_to_scan = list(live_game_ids)
    changed_game_ids: list[int] = []
    changes_status: int | None = None
    error: str | None = None
    checkpoint_saved = False
    scan_count = _safe_int(checkpoint.get('scan_count', 0), 0) + 1
    reconcile_triggered = False

    if settings.live_scanner_mode.lower() == 'changes':
        since = (
            updated_since
            or checkpoint.get('updated_since')
            or _default_updated_since(settings.game_changes_lookback_seconds)
        )

        try:
            changes = provider.fetch_game_changes(str(since))
            changes_status = changes.status_code
            changed_game_ids = extract_changed_game_ids(changes.payload)
            live_lookup = set(live_game_ids)
            games_to_scan = [game_pk for game_pk in changed_game_ids if game_pk in live_lookup]

            reconcile_triggered = scan_count % settings.reconcile_every_n_scans == 0
            if reconcile_triggered:
                games_to_scan = list(live_game_ids)
        except RuntimeError as cause:
            error = str(cause)
            save_checkpoint(
                settings.scanner_checkpoint_path,
                {
                    'updated_since': checkpoint.get('updated_since'),
                    'last_success_at': checkpoint.get('last_success_at'),
                    'consecutive_failures': _safe_int(checkpoint.get('consecutive_failures', 0), 0)
                    + 1,
                    'scan_count': scan_count,
                },
            )
            checkpoint_saved = True
            return {
                'status': 'degraded',
                'scanner_mode': settings.live_scanner_mode.lower(),
                'schedule_status': schedule.status_code,
                'schedule_dates': len(schedule.payload.get('dates', [])),
                'live_games': live_game_ids,
                'changed_games': [],
                'updated_since': since,
                'changes_status': None,
                'games_scanned': [],
                'event_count': 0,
                'update_count': 0,
                'snapshot': previous_snapshot or set(),
                'scanner_lag_seconds': _lag_seconds(str(since)),
                'changed_games_count': 0,
                'feed_failures_count': 0,
                'checkpoint_saved': checkpoint_saved,
                'scanner_scan_count': scan_count,
                'reconcile_triggered': False,
                'reconcile_games_count': 0,
                'delta_payload': build_delta_payload([], player_positions={}),
                'error': error,
            }
    else:
        since = None

    all_events: list[dict[str, int | str]] = []
    feed_failures_count = 0
    for game_pk in games_to_scan:
        try:
            feed = provider.fetch_live_game_feed(game_pk)
            all_events.extend(extract_stat_change_events(feed.payload))
        except RuntimeError:
            feed_failures_count += 1

    updates, snapshot = diff_player_updates(all_events, previous_snapshot or set())

    if settings.live_scanner_mode.lower() == 'changes':
        now_iso = _format_utc(_utc_now())
        save_checkpoint(
            settings.scanner_checkpoint_path,
            {
                'updated_since': now_iso,
                'last_success_at': now_iso,
                'consecutive_failures': 0,
                'scan_count': scan_count,
            },
        )
        checkpoint_saved = True

    delta_payload = build_delta_payload(updates, player_positions={})

    return {
        'status': 'ok',
        'scanner_mode': settings.live_scanner_mode.lower(),
        'schedule_status': schedule.status_code,
        'schedule_dates': len(schedule.payload.get('dates', [])),
        'live_games': live_game_ids,
        'changed_games': changed_game_ids,
        'updated_since': since,
        'changes_status': changes_status,
        'games_scanned': games_to_scan,
        'event_count': len(all_events),
        'update_count': len(updates),
        'snapshot': snapshot,
        'scanner_lag_seconds': _lag_seconds(str(since) if since else None),
        'changed_games_count': len(changed_game_ids),
        'feed_failures_count': feed_failures_count,
        'checkpoint_saved': checkpoint_saved,
        'scanner_scan_count': scan_count,
        'reconcile_triggered': reconcile_triggered,
        'reconcile_games_count': len(games_to_scan) if reconcile_triggered else 0,
        'delta_payload': delta_payload,
        'error': error,
    }


def main() -> None:
    run_once()


if __name__ == '__main__':
    main()
