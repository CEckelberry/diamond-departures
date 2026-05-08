from apps.ingest.app.live_delta import build_delta_payload


def test_build_delta_payload_extracts_changed_players_and_views() -> None:
    updates = [
        {'game_pk': 662001, 'at_bat_index': 1, 'player_id': 660271, 'event_type': 'single'},
        {'game_pk': 662001, 'at_bat_index': 2, 'player_id': 605141, 'event_type': 'home_run'},
    ]

    payload = build_delta_payload(updates, player_positions={660271: {'SS'}, 605141: {'OF'}})

    assert payload['changed_player_ids'] == [605141, 660271]
    assert ('hitters', 'wRC+') in payload['affected_views']
    assert ('hitters', 'OPS') in payload['affected_views']
    assert ('hitters_ss', 'wRC+') in payload['affected_views']
    assert ('hitters_of', 'OPS') in payload['affected_views']


def test_build_delta_payload_empty_updates() -> None:
    payload = build_delta_payload([], player_positions={})

    assert payload['changed_player_ids'] == []
    assert payload['affected_views'] == []
