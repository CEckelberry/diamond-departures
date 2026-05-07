import json
from pathlib import Path

from apps.ingest.app.schedule import extract_live_game_ids


def test_extract_live_game_ids_from_schedule_fixture() -> None:
    fixture = Path(__file__).parent / "fixtures" / "schedule_live.json"
    payload = json.loads(fixture.read_text(encoding="utf-8"))

    assert extract_live_game_ids(payload) == [662001]
