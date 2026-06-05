from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from .players import PlayerDetailReader, PlayerHistoryReader
from .users import UserUpsert
from .watchlist import WatchlistLister, WatchlistAdder, WatchlistRemover
from .watch_boards import BoardLister, BoardCreator, BoardGetter, BoardRenamer, BoardDeleter, BoardPlayerAdder, BoardPlayerRemover
from .alerts import AlertLister, AlertCreator, AlertDeleter


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


def postgres_watchlist_lister(database_url: str) -> WatchlistLister:
    def _list(user_id: str) -> list[dict]:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT user_id::text, player_id FROM watchlist_players WHERE user_id = %s ORDER BY added_at DESC",
                    (user_id,),
                )
                return [dict(r) for r in cur.fetchall()]
    return _list


def postgres_watchlist_adder(database_url: str) -> WatchlistAdder:
    def _add(user_id: str, player_id: int) -> None:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO watchlist_players (user_id, player_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (user_id, player_id),
                )
    return _add


def postgres_watchlist_remover(database_url: str) -> WatchlistRemover:
    def _remove(user_id: str, player_id: int) -> bool:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM watchlist_players WHERE user_id = %s AND player_id = %s",
                    (user_id, player_id),
                )
                return (cur.rowcount or 0) > 0
    return _remove


def postgres_board_lister(database_url: str) -> BoardLister:
    def _list(user_id: str) -> list[dict]:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id::text, user_id::text, name FROM watch_boards WHERE user_id = %s ORDER BY created_at ASC", (user_id,))
                return [dict(r) for r in cur.fetchall()]
    return _list


def postgres_board_creator(database_url: str) -> BoardCreator:
    def _create(user_id: str, name: str) -> dict:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("INSERT INTO watch_boards (user_id, name) VALUES (%s, %s) RETURNING id::text, user_id::text, name", (user_id, name))
                return dict(cur.fetchone())
    return _create


def postgres_board_getter(database_url: str) -> BoardGetter:
    def _get(board_id: str, user_id: str) -> dict | None:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id::text, user_id::text, name FROM watch_boards WHERE id = %s AND user_id = %s", (board_id, user_id))
                row = cur.fetchone()
                if not row:
                    return None
                cur.execute("SELECT player_id FROM watch_board_players WHERE board_id = %s", (board_id,))
                players = [r["player_id"] for r in cur.fetchall()]
                return {**dict(row), "players": players}
    return _get


def postgres_board_renamer(database_url: str) -> BoardRenamer:
    def _rename(board_id: str, user_id: str, name: str) -> bool:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE watch_boards SET name = %s, updated_at = now() WHERE id = %s AND user_id = %s", (name, board_id, user_id))
                return (cur.rowcount or 0) > 0
    return _rename


def postgres_board_deleter(database_url: str) -> BoardDeleter:
    def _delete(board_id: str, user_id: str) -> bool:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM watch_boards WHERE id = %s AND user_id = %s", (board_id, user_id))
                return (cur.rowcount or 0) > 0
    return _delete


def postgres_board_player_adder(database_url: str) -> BoardPlayerAdder:
    def _add(board_id: str, user_id: str, player_id: int) -> bool:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM watch_boards WHERE id = %s AND user_id = %s", (board_id, user_id))
                if not cur.fetchone():
                    return False
                cur.execute("INSERT INTO watch_board_players (board_id, player_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (board_id, player_id))
                return True
    return _add


def postgres_board_player_remover(database_url: str) -> BoardPlayerRemover:
    def _remove(board_id: str, user_id: str, player_id: int) -> bool:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM watch_board_players WHERE board_id = %s AND player_id = %s", (board_id, player_id))
                return (cur.rowcount or 0) > 0
    return _remove


def postgres_alert_lister(database_url: str) -> AlertLister:
    def _list(user_id: str) -> list[dict]:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id::text, user_id::text, player_id, stat_name, threshold, direction FROM email_alerts WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
                return [{**dict(r), "threshold": float(r["threshold"])} for r in cur.fetchall()]
    return _list


def postgres_alert_creator(database_url: str) -> AlertCreator:
    def _create(user_id: str, player_id: int, stat_name: str, threshold: float, direction: str) -> dict:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO email_alerts (user_id, player_id, stat_name, threshold, direction) VALUES (%s, %s, %s, %s, %s) RETURNING id::text, user_id::text, player_id, stat_name, threshold, direction",
                    (user_id, player_id, stat_name, threshold, direction),
                )
                r = cur.fetchone()
                return {**dict(r), "threshold": float(r["threshold"])}
    return _create


def postgres_alert_deleter(database_url: str) -> AlertDeleter:
    def _delete(alert_id: str, user_id: str) -> bool:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM email_alerts WHERE id = %s AND user_id = %s", (alert_id, user_id))
                return (cur.rowcount or 0) > 0
    return _delete
