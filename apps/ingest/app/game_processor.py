from __future__ import annotations

STAT_CHANGING_EVENTS = {
    "single",
    "double",
    "triple",
    "home_run",
    "walk",
    "strikeout",
    "hit_by_pitch",
    "field_error",
}


def extract_stat_change_events(feed_payload: dict) -> list[dict[str, int | str]]:
    game_pk = int(feed_payload.get("gamePk", 0))
    all_plays = feed_payload.get("liveData", {}).get("plays", {}).get("allPlays", [])
    events: list[dict[str, int | str]] = []

    for play in all_plays:
        event_type = str(play.get("result", {}).get("eventType", "")).lower()
        if event_type not in STAT_CHANGING_EVENTS:
            continue

        batter = play.get("matchup", {}).get("batter", {})
        player_id = batter.get("id")
        at_bat_index = play.get("atBatIndex")
        if player_id is None or at_bat_index is None:
            continue

        events.append(
            {
                "game_pk": game_pk,
                "at_bat_index": int(at_bat_index),
                "player_id": int(player_id),
                "event_type": event_type,
            }
        )

    return events
