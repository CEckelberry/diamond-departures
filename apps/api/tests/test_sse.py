from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone

import pytest

from apps.api.app.sse import BoardSSEHub


@pytest.mark.anyio
async def test_sse_stream_sends_snapshot_immediately() -> None:
    now = datetime.now(timezone.utc).isoformat()
    rows = [
        {
            "rank": 1,
            "player_id": 1,
            "player_name": "Player One",
            "team_abbr": "SD",
            "headshot_url": "https://example.test/1.png",
            "position": "SS",
            "stat_value": 155.0,
            "refreshed_at": now,
        },
        {
            "rank": 2,
            "player_id": 2,
            "player_name": "Player Two",
            "team_abbr": "NYY",
            "headshot_url": "https://example.test/2.png",
            "position": "RF",
            "stat_value": 149.0,
            "refreshed_at": now,
        },
    ]

    hub = BoardSSEHub(heartbeat_seconds=1.0)
    stream = hub.stream("hitters", "wRC+", rows)

    raw = await asyncio.wait_for(stream.__anext__(), timeout=1.0)
    lines = [ln for ln in raw.strip().split("\n") if ln]
    event = lines[0].split(": ", 1)[1]
    payload = json.loads(lines[1].split(": ", 1)[1])

    assert event == "snapshot"
    assert payload["view"] == "hitters"
    assert payload["sort"] == "wRC+"
    assert len(payload["entries"]) == 2

    await stream.aclose()


@pytest.mark.anyio
async def test_sse_stream_emits_delta_after_publish() -> None:
    now = datetime.now(timezone.utc).isoformat()
    rows = [
        {
            "rank": 1,
            "player_id": 1,
            "player_name": "Player One",
            "team_abbr": "SD",
            "headshot_url": "https://example.test/1.png",
            "position": "SS",
            "stat_value": 155.0,
            "refreshed_at": now,
        },
        {
            "rank": 2,
            "player_id": 2,
            "player_name": "Player Two",
            "team_abbr": "NYY",
            "headshot_url": "https://example.test/2.png",
            "position": "RF",
            "stat_value": 149.0,
            "refreshed_at": now,
        },
    ]

    hub = BoardSSEHub(heartbeat_seconds=1.0)
    stream = hub.stream("hitters", "wRC+", rows)
    await asyncio.wait_for(stream.__anext__(), timeout=1.0)

    hub.publish_snapshot(
        "hitters",
        "wRC+",
        [
            {**rows[0], "rank": 2, "stat_value": 150.0},
            {**rows[1], "rank": 1, "stat_value": 160.0},
        ],
    )

    raw = await asyncio.wait_for(stream.__anext__(), timeout=1.0)
    lines = [ln for ln in raw.strip().split("\n") if ln]
    event = lines[0].split(": ", 1)[1]
    payload = json.loads(lines[1].split(": ", 1)[1])

    assert event == "delta"
    assert payload["changes"]
    assert payload["changes"][0]["player_id"] in {1, 2}

    await stream.aclose()


@pytest.mark.anyio
async def test_sse_stream_emits_heartbeat_when_idle() -> None:
    now = datetime.now(timezone.utc).isoformat()
    rows = [
        {
            "rank": 1,
            "player_id": 1,
            "player_name": "Player One",
            "team_abbr": "SD",
            "headshot_url": "https://example.test/1.png",
            "position": "SS",
            "stat_value": 155.0,
            "refreshed_at": now,
        }
    ]

    hub = BoardSSEHub(heartbeat_seconds=0.01)
    stream = hub.stream("hitters", "wRC+", rows)

    await asyncio.wait_for(stream.__anext__(), timeout=1.0)
    raw = await asyncio.wait_for(stream.__anext__(), timeout=1.0)

    lines = [ln for ln in raw.strip().split("\n") if ln]
    event = lines[0].split(": ", 1)[1]
    payload = json.loads(lines[1].split(": ", 1)[1])

    assert event == "heartbeat"
    assert isinstance(payload["ts"], int)

    await stream.aclose()


@pytest.mark.anyio
async def test_sse_disconnect_cleans_up_connection_registration() -> None:
    now = datetime.now(timezone.utc).isoformat()
    rows = [
        {
            "rank": 1,
            "player_id": 1,
            "player_name": "Player One",
            "team_abbr": "SD",
            "headshot_url": "https://example.test/1.png",
            "position": "SS",
            "stat_value": 155.0,
            "refreshed_at": now,
        }
    ]

    hub = BoardSSEHub(heartbeat_seconds=1.0)
    stream = hub.stream("hitters", "wRC+", rows)

    await asyncio.wait_for(stream.__anext__(), timeout=1.0)
    assert hub.connection_count("hitters", "wRC+") == 1

    await stream.aclose()
    assert hub.connection_count("hitters", "wRC+") == 0
