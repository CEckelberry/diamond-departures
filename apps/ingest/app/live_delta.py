from __future__ import annotations

from .leaderboards import map_affected_views


def build_delta_payload(
    updates: list[dict[str, int | str]],
    *,
    player_positions: dict[int, set[str]],
) -> dict[str, object]:
    changed_player_ids = sorted({int(update['player_id']) for update in updates if 'player_id' in update})

    updated_stats_by_player: dict[int, set[str]] = {}
    for player_id in changed_player_ids:
        updated_stats_by_player[player_id] = {'wRC+', 'OPS'}

    affected = sorted(
        map_affected_views(
            updated_stats_by_player=updated_stats_by_player,
            player_positions=player_positions,
        )
    )

    return {
        'changed_player_ids': changed_player_ids,
        'affected_views': affected,
    }
