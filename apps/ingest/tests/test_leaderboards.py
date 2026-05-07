from __future__ import annotations

from datetime import datetime, timezone

from apps.ingest.app.leaderboards import (
    LeaderboardStore,
    PlayerLeaderboardSnapshot,
    map_affected_views,
    recompute_view,
)


def test_map_affected_views_from_updated_stat_names_and_positions() -> None:
    affected = map_affected_views(
        updated_stats_by_player={660271: {"wRC+"}, 605141: {"OPS"}},
        player_positions={660271: {"SS", "2B"}, 605141: {"OF"}},
    )

    assert ("hitters", "wRC+") in affected
    assert ("hitters", "OPS") in affected
    assert ("hitters_ss", "wRC+") in affected
    assert ("hitters_of", "OPS") in affected


def test_recompute_view_replaces_with_exact_top_100_ranked_rows() -> None:
    store = LeaderboardStore()
    snapshots = [
        PlayerLeaderboardSnapshot(player_id=1000 + idx, stat_name="wRC+", stat_value=float(200 - idx), eligible_pos={"SS"})
        for idx in range(120)
    ]

    rows = recompute_view(
        store=store,
        view_key="hitters",
        sort_stat="wRC+",
        snapshots=snapshots,
        refreshed_at=datetime(2026, 5, 7, tzinfo=timezone.utc),
    )

    assert len(rows) == 100
    assert len(store.get_view_rows(view_key="hitters", sort_stat="wRC+")) == 100
    assert rows[0].player_id == 1000
    assert rows[-1].rank == 100


def test_position_filtered_view_only_contains_eligible_players() -> None:
    store = LeaderboardStore()
    snapshots = [
        PlayerLeaderboardSnapshot(player_id=1, stat_name="wRC+", stat_value=140.0, eligible_pos={"SS", "2B"}),
        PlayerLeaderboardSnapshot(player_id=2, stat_name="wRC+", stat_value=145.0, eligible_pos={"1B"}),
        PlayerLeaderboardSnapshot(player_id=3, stat_name="wRC+", stat_value=120.0, eligible_pos={"SS"}),
    ]

    rows = recompute_view(
        store=store,
        view_key="hitters_ss",
        sort_stat="wRC+",
        snapshots=snapshots,
        refreshed_at=datetime(2026, 5, 7, tzinfo=timezone.utc),
        required_position="SS",
    )

    assert [row.player_id for row in rows] == [1, 3]
