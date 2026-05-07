import json
from pathlib import Path

from apps.ingest.app.game_processor import extract_stat_change_events
from apps.ingest.app.state_diff import diff_player_updates


def test_diff_player_updates_idempotency() -> None:
    fixture = Path(__file__).parent / "fixtures" / "game_feed_events.json"
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    events = extract_stat_change_events(payload)

    first_updates, snapshot = diff_player_updates(events, previous_snapshot=set())
    second_updates, second_snapshot = diff_player_updates(events, previous_snapshot=snapshot)

    assert len(first_updates) == 5
    assert len(second_updates) == 0
    assert second_snapshot == snapshot
