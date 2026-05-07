from __future__ import annotations


def _event_key(event: dict[str, int | str]) -> str:
    return f"{event['game_pk']}:{event['at_bat_index']}:{event['player_id']}"


def diff_player_updates(
    events: list[dict[str, int | str]], previous_snapshot: set[str]
) -> tuple[list[dict[str, int | str]], set[str]]:
    current_snapshot = {_event_key(event) for event in events}
    new_keys = current_snapshot - previous_snapshot

    updates = [event for event in events if _event_key(event) in new_keys]
    return updates, current_snapshot
