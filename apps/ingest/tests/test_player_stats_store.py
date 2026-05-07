from __future__ import annotations

from datetime import datetime, timedelta, timezone

from apps.ingest.app.player_stats_store import PlayerStatRecord, PlayerStatsStore


def test_append_only_closes_previous_row_and_creates_new_current_row() -> None:
    store = PlayerStatsStore()
    t0 = datetime(2026, 5, 7, 1, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(minutes=10)

    first = store.upsert_stat(
        player_id=42,
        stat_name="wRC+",
        stat_value=120.0,
        season=2026,
        source="mlb-api",
        observed_at=t0,
    )
    second = store.upsert_stat(
        player_id=42,
        stat_name="wRC+",
        stat_value=131.0,
        season=2026,
        source="mlb-api",
        observed_at=t1,
    )

    assert first.changed is True
    assert second.changed is True

    history = store.get_history(player_id=42, stat_name="wRC+", season=2026)
    assert len(history) == 2
    assert history[0].valid_to == t1
    assert history[1].valid_to is None
    assert history[1].stat_value == 131.0


def test_same_value_is_noop_and_creates_no_new_row() -> None:
    store = PlayerStatsStore()
    t0 = datetime(2026, 5, 7, 1, 0, tzinfo=timezone.utc)

    store.upsert_stat(
        player_id=8,
        stat_name="OPS",
        stat_value=0.801,
        season=2026,
        source="mlb-api",
        observed_at=t0,
    )
    second = store.upsert_stat(
        player_id=8,
        stat_name="OPS",
        stat_value=0.801,
        season=2026,
        source="mlb-api",
        observed_at=t0 + timedelta(minutes=1),
    )

    history = store.get_history(player_id=8, stat_name="OPS", season=2026)
    assert second.changed is False
    assert len(history) == 1


def test_current_lookup_returns_one_open_row() -> None:
    store = PlayerStatsStore(
        seed=[
            PlayerStatRecord(
                player_id=9,
                stat_name="wRC+",
                stat_value=110.0,
                valid_from=datetime(2026, 5, 6, tzinfo=timezone.utc),
                valid_to=None,
                source="seed",
                season=2026,
            )
        ]
    )

    current = store.get_current(player_id=9, stat_name="wRC+", season=2026)
    assert current is not None
    assert current.stat_value == 110.0
