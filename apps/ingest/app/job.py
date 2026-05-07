from __future__ import annotations

from .config import load_settings
from .game_processor import extract_stat_change_events
from .mlb_client import MLBApiClient
from .schedule import extract_live_game_ids
from .state_diff import diff_player_updates
from .store import init_store


def run_once(previous_snapshot: set[str] | None = None) -> dict[str, object]:
    settings = load_settings()
    client = MLBApiClient(
        base_url=settings.mlb_api_url,
        timeout_seconds=settings.request_timeout_seconds,
        max_retries=settings.max_http_retries,
        retry_backoff_seconds=settings.retry_backoff_seconds,
    )
    store = init_store(settings.database_url)
    schedule = client.get_json("/api/v1/schedule")
    _ = store.session_factory()

    live_game_ids = extract_live_game_ids(schedule.payload)
    all_events: list[dict[str, int | str]] = []
    for game_pk in live_game_ids:
        feed = client.get_json(f"/api/v1/game/{game_pk}/feed/live")
        all_events.extend(extract_stat_change_events(feed.payload))

    updates, snapshot = diff_player_updates(all_events, previous_snapshot or set())

    return {
        "status": "ok",
        "schedule_status": schedule.status_code,
        "schedule_dates": len(schedule.payload.get("dates", [])),
        "live_games": live_game_ids,
        "event_count": len(all_events),
        "update_count": len(updates),
        "snapshot": snapshot,
    }


def main() -> None:
    run_once()


if __name__ == "__main__":
    main()
