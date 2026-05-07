from __future__ import annotations

from datetime import datetime, timezone

from apps.api.app.cache import LeaderboardCache


def test_cache_loads_all_keys_on_startup() -> None:
    called = {"count": 0}

    def loader() -> dict[tuple[str, str], list[dict[str, object]]]:
        called["count"] += 1
        return {
            ("hitters", "wRC+"): [
                {
                    "rank": 1,
                    "player_id": 1,
                    "player_name": "Player One",
                    "team_abbr": "SD",
                    "headshot_url": "https://example.test/1.png",
                    "position": "SS",
                    "stat_value": 140.0,
                    "refreshed_at": datetime.now(timezone.utc).isoformat(),
                }
            ]
        }

    cache = LeaderboardCache(load_all=loader)
    cache.load_startup()

    assert called["count"] == 1
    assert len(cache.get("hitters", "wRC+")) == 1


def test_cache_get_returns_copy() -> None:
    cache = LeaderboardCache(load_all=lambda: {("hitters", "wRC+"): [{"rank": 1}]})
    cache.load_startup()

    rows = cache.get("hitters", "wRC+")
    rows.append({"rank": 2})

    assert cache.get("hitters", "wRC+") == [{"rank": 1}]


def test_cache_invalidate_refreshes_single_key() -> None:
    state = {"value": 1}

    cache = LeaderboardCache(load_all=lambda: {("hitters", "wRC+"): [{"rank": state["value"]}]})
    cache.load_startup()

    state["value"] = 2
    cache.invalidate("hitters", "wRC+", refresh_one=lambda v, s: [{"rank": state["value"]}])

    assert cache.get("hitters", "wRC+") == [{"rank": 2}]
