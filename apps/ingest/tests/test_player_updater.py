from __future__ import annotations

from datetime import datetime, timezone

from apps.ingest.app.player_stats_store import PlayerStatsStore
from apps.ingest.app.player_updater import BattingLine, LeagueContextInputs, update_player_stats


def test_update_player_stats_writes_derived_ops_and_wrc_plus() -> None:
    store = PlayerStatsStore()
    line = BattingLine(
        at_bats=200,
        hits=62,
        doubles=14,
        triples=2,
        home_runs=11,
        walks=24,
        intentional_walks=1,
        hit_by_pitch=3,
        sacrifice_flies=4,
    )

    result = update_player_stats(
        player_id=660271,
        season=2026,
        batting_line=line,
        store=store,
        observed_at=datetime(2026, 5, 7, tzinfo=timezone.utc),
        context=LeagueContextInputs(
            league_woba=0.312,
            woba_scale=1.25,
            league_runs_per_pa=0.118,
            park_factor=0.98,
        ),
    )

    assert "OPS" in result.changed_stats
    assert "wRC+" in result.changed_stats

    ops_current = store.get_current(player_id=660271, stat_name="OPS", season=2026)
    wrc_current = store.get_current(player_id=660271, stat_name="wRC+", season=2026)
    assert ops_current is not None
    assert wrc_current is not None


def test_unchanged_line_does_not_create_more_rows() -> None:
    store = PlayerStatsStore()
    line = BattingLine(
        at_bats=150,
        hits=45,
        doubles=8,
        triples=1,
        home_runs=7,
        walks=21,
        intentional_walks=0,
        hit_by_pitch=1,
        sacrifice_flies=2,
    )
    observed_at = datetime(2026, 5, 7, tzinfo=timezone.utc)
    context = LeagueContextInputs(
        league_woba=0.312,
        woba_scale=1.25,
        league_runs_per_pa=0.118,
        park_factor=1.0,
    )

    first = update_player_stats(
        player_id=605141,
        season=2026,
        batting_line=line,
        store=store,
        observed_at=observed_at,
        context=context,
    )
    second = update_player_stats(
        player_id=605141,
        season=2026,
        batting_line=line,
        store=store,
        observed_at=observed_at,
        context=context,
    )

    assert first.changed_stats
    assert second.changed_stats == []
    assert len(store.get_history(player_id=605141, stat_name="wRC+", season=2026)) == 1
