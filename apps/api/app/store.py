from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from .players import PlayerDetailReader, PlayerHistoryReader
from .users import UserUpsert


def postgres_health_check(database_url: str) -> Callable[[], bool]:
    def _health() -> bool:
        try:
            conn = psycopg2.connect(database_url, connect_timeout=3)
            conn.close()
            return True
        except Exception as e:
            logging.getLogger("apps.api.store").error("db health check failed: %s", e)
            return False

    return _health


def postgres_board_reader(database_url: str) -> Callable[[str, str, int], list[dict[str, Any]]]:
    def _read(view: str, sort: str, season: int = 2026) -> list[dict[str, Any]]:
        try:
            with psycopg2.connect(database_url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT
                            lv.rank,
                            p.id as player_id,
                            p.full_name as player_name,
                            t.abbr as team_abbr,
                            p.headshot_url,
                            p.primary_pos as position,
                            lv.stat_value,
                            lv.refreshed_at,
                            COALESCE(
                                jsonb_object_agg(ps.stat_name, ps.stat_value)
                                    FILTER (WHERE ps.stat_name IS NOT NULL),
                                '{}'::jsonb
                            ) as additional_stats
                        FROM leaderboard_views lv
                        JOIN players p ON lv.player_id = p.id
                        JOIN teams t ON p.team_id = t.id
                        LEFT JOIN player_stats ps
                            ON ps.player_id = p.id
                           AND ps.season = lv.season
                           AND ps.valid_to IS NULL
                        WHERE lv.view_key = %s
                          AND lv.sort_stat = %s
                          AND lv.season = %s
                        GROUP BY lv.rank, p.id, p.full_name, t.abbr,
                                 p.headshot_url, p.primary_pos,
                                 lv.stat_value, lv.refreshed_at
                        ORDER BY lv.rank ASC
                        LIMIT 50
                    """, (view, sort, season))
                    return list(cur.fetchall())
        except Exception as e:
            logging.getLogger("apps.api.store").error("failed to read board: %s", e)
            return []
    return _read


def postgres_player_detail_reader(database_url: str) -> PlayerDetailReader:
    def _read(player_id: int) -> dict[str, Any] | None:
        try:
            with psycopg2.connect(database_url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT p.id, p.full_name, p.short_name, p.primary_pos, p.headshot_url,
                               t.abbr as team_abbr
                        FROM players p
                        JOIN teams t ON p.team_id = t.id
                        WHERE p.id = %s
                    """, (player_id,))
                    row = cur.fetchone()
                    if row is None:
                        return None

                    cur.execute("""
                        SELECT stat_name, stat_value
                        FROM player_stats
                        WHERE player_id = %s AND valid_to IS NULL
                    """, (player_id,))
                    stats = {r["stat_name"]: float(r["stat_value"]) for r in cur.fetchall()}

            return {
                "player": {
                    "id": row["id"],
                    "name": row["full_name"],
                    "team_abbr": row["team_abbr"],
                    "headshot_url": row["headshot_url"] or "",
                    "position": row["primary_pos"] or "",
                },
                "season_totals": stats,
                "stat_line": stats,
                "recent_games": [],
            }
        except Exception as e:
            logging.getLogger("apps.api.store").error("failed to read player detail %s: %s", player_id, e)
            return None

    return _read


def postgres_player_history_reader(database_url: str) -> PlayerHistoryReader:
    def _read(player_id: int, stat: str) -> list[dict[str, Any]] | None:
        try:
            with psycopg2.connect(database_url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("SELECT 1 FROM players WHERE id = %s", (player_id,))
                    if cur.fetchone() is None:
                        return None

                    cur.execute("""
                        SELECT valid_from as timestamp, stat_value as value
                        FROM player_stats
                        WHERE player_id = %s AND stat_name = %s
                        ORDER BY valid_from ASC
                    """, (player_id, stat))
                    return [{"timestamp": str(r["timestamp"]), "value": float(r["value"])}
                            for r in cur.fetchall()]
        except Exception as e:
            logging.getLogger("apps.api.store").error("failed to read player history %s/%s: %s", player_id, stat, e)
            return None

    return _read


def postgres_mark_premium(database_url: str) -> Callable[[str], None]:
    def _mark(user_id: str) -> None:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET is_premium = true, purchased_at = now() WHERE id = %s",
                    (user_id,),
                )
    return _mark


def postgres_user_upsert(database_url: str) -> UserUpsert:
    def _upsert(user_id: str, email: str, name: str | None, avatar_url: str | None) -> dict:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO users (id, email, name, avatar_url, last_seen_at)
                    VALUES (%s, %s, %s, %s, now())
                    ON CONFLICT (id) DO UPDATE SET
                        email        = EXCLUDED.email,
                        name         = COALESCE(EXCLUDED.name, users.name),
                        avatar_url   = COALESCE(EXCLUDED.avatar_url, users.avatar_url),
                        last_seen_at = now()
                    RETURNING id, email, name, avatar_url, is_premium, purchased_at, created_at, last_seen_at
                    """,
                    (user_id, email, name, avatar_url),
                )
                row = cur.fetchone()
                return {
                    "id": str(row["id"]),
                    "email": row["email"],
                    "name": row["name"],
                    "avatar_url": row["avatar_url"],
                    "is_premium": row["is_premium"],
                    "purchased_at": row["purchased_at"].isoformat() if row["purchased_at"] else None,
                }
    return _upsert
