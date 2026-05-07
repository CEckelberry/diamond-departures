import json
from pathlib import Path

from apps.ingest.app.game_processor import extract_stat_change_events


def test_extract_stat_change_events_from_feed_fixture() -> None:
    fixture = Path(__file__).parent / "fixtures" / "game_feed_events.json"
    payload = json.loads(fixture.read_text(encoding="utf-8"))

    events = extract_stat_change_events(payload)

    assert len(events) == 5
    assert events[0]["game_pk"] == 662001
    assert events[0]["at_bat_index"] == 1
    assert events[0]["player_id"] == 660271
