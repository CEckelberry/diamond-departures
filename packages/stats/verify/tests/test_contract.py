import json
from pathlib import Path


def test_curated_dataset_contract_shape() -> None:
    data_path = Path(__file__).resolve().parents[1] / "data.json"
    payload = json.loads(data_path.read_text(encoding="utf-8"))

    assert payload["metadata"]["capture_date"]
    assert payload["metadata"]["tolerance_percent"] == 0.5

    entries = payload["entries"]
    assert len(entries) >= 4

    for entry in entries:
      assert entry["player_id"]
      assert entry["player_name"]
      assert isinstance(entry["season"], int)
      assert "fangraphs" in entry["source"]
      assert "baseball_reference" in entry["source"]
      assert entry["expected"]
      assert all(isinstance(v, (int, float)) for v in entry["expected"].values())
