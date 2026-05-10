from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor


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


def postgres_board_reader(database_url: str) -> Callable[[str, str], list[dict[str, Any]]]:
    def _read(view: str, sort: str) -> list[dict[str, Any]]:
        try:
            with psycopg2.connect(database_url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # view_key corresponds to the view param
                    # sort_stat corresponds to the sort param
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
                            COALESCE(jsonb_object_agg(ps.stat_name, ps.stat_value) FILTER (WHERE ps.stat_name IS NOT NULL), '{}'::jsonb) as additional_stats
                        FROM leaderboard_views lv
                        JOIN players p ON lv.player_id = p.id
                        JOIN teams t ON p.team_id = t.id
                        LEFT JOIN player_stats ps ON ps.player_id = p.id AND ps.valid_to IS NULL
                        WHERE lv.view_key = %s AND lv.sort_stat = %s
                        GROUP BY lv.rank, p.id, p.full_name, t.abbr, p.headshot_url, p.primary_pos, lv.stat_value, lv.refreshed_at
                        ORDER BY lv.rank ASC
                        LIMIT 50
""", (view, sort))
                    return list(cur.fetchall())
        except Exception as e:
            logging.getLogger("apps.api.store").error("failed to read board: %s", e)
            return []

    return _read
