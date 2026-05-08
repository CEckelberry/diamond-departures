from __future__ import annotations

from datetime import UTC, datetime, timedelta

from .config import load_settings
from .game_processor import extract_stat_change_events
from .provider import build_provider
from .schedule import extract_changed_game_ids, extract_live_game_ids
from .state_diff import diff_player_updates
from .store import init_store


def _default_updated_since(lookback_seconds: int) -> str:
    point = datetime.now(UTC) - timedelta(seconds=lookback_seconds)
    return point.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_once(
    previous_snapshot: set[str] | None = None,
    updated_since: str | None = None,
) -> dict[str, object]:
    settings = load_settings()
    provider = build_provider(settings)
    store = init_store(settings.database_url)
    schedule = provider.fetch_schedule()
    _ = store.session_factory()

    live_game_ids = extract_live_game_ids(schedule.payload)
    games_to_scan = list(live_game_ids)

    if settings.live_scanner_mode.lower() == "changes":
        since = updated_since or _default_updated_since(settings.game_changes_lookback_seconds)
        changes = provider.fetch_game_changes(since)
        changed_game_ids = extract_changed_game_ids(changes.payload)
        live_lookup = set(live_game_ids)
        games_to_scan = [game_pk for game_pk in changed_game_ids if game_pk in live_lookup]
    else:
        since = None
        changes = None
        changed_game_ids = []

    all_events: list[dict[str, int | str]] = []
    for game_pk in games_to_scan:
        feed = provider.fetch_live_game_feed(game_pk)
        all_events.extend(extract_stat_change_events(feed.payload))

    updates, snapshot = diff_player_updates(all_events, previous_snapshot or set())

    return {
        "status": "ok",
        "scanner_mode": settings.live_scanner_mode.lower(),
        "schedule_status": schedule.status_code,
        "schedule_dates": len(schedule.payload.get("dates", [])),
        "live_games": live_game_ids,
        "changed_games": changed_game_ids,
        "updated_since": since,
        "changes_status": changes.status_code if changes else None,
        "games_scanned": games_to_scan,
        "event_count": len(all_events),
        "update_count": len(updates),
        "snapshot": snapshot,
    }


def main() -> None:
    run_once()


if __name__ == "__main__":
    main()
