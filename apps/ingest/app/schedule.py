from __future__ import annotations


def extract_live_game_ids(schedule_payload: dict) -> list[int]:
    live_ids: list[int] = []

    for day in schedule_payload.get("dates", []):
        for game in day.get("games", []):
            status = game.get("status", {})
            abstract_state = str(status.get("abstractGameState", "")).lower()
            coded_state = str(status.get("codedGameState", "")).upper()
            if abstract_state == "live" or coded_state == "I":
                live_ids.append(int(game["gamePk"]))

    return live_ids


def extract_changed_game_ids(changes_payload: dict) -> list[int]:
    changed_ids: list[int] = []

    games = changes_payload.get("games", [])
    for game in games:
        game_pk = game.get("gamePk")
        if game_pk is None:
            continue
        try:
            changed_ids.append(int(game_pk))
        except (TypeError, ValueError):
            continue

    return changed_ids
