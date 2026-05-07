from __future__ import annotations

from apps.ingest.app.drift import DriftDetector, shape_hash


def test_shape_hash_stable_when_only_values_change() -> None:
    first = {
        "gamePk": 1,
        "liveData": {"plays": {"allPlays": [{"atBatIndex": 1, "result": {"eventType": "single"}}]}},
    }
    second = {
        "gamePk": 662001,
        "liveData": {"plays": {"allPlays": [{"atBatIndex": 99, "result": {"eventType": "double"}}]}},
    }

    assert shape_hash(first) == shape_hash(second)


def test_drift_detector_warns_when_schema_adds_new_key() -> None:
    logs: list[tuple[str, str]] = []

    detector = DriftDetector(log_fn=lambda level, message, **_: logs.append((level, message)))
    detector.evaluate(source="schedule", payload={"dates": []})
    result = detector.evaluate(source="schedule", payload={"dates": [], "newField": {"nested": True}})

    assert result.drifted is True
    assert any(level == "WARN" for level, _ in logs)


def test_drift_detector_errors_when_required_key_missing() -> None:
    logs: list[tuple[str, str]] = []

    detector = DriftDetector(log_fn=lambda level, message, **_: logs.append((level, message)))
    result = detector.evaluate(
        source="game-feed",
        payload={"gamePk": 662001, "liveData": {}},
        required_paths=["liveData.plays.allPlays"],
    )

    assert result.parse_error is True
    assert any(level == "ERROR" for level, _ in logs)
