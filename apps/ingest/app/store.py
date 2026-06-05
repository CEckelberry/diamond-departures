from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import psycopg2
from psycopg2.extras import execute_values


@dataclass(frozen=True)
class StoreContext:
    database_url: str

    def save_players(self, players: list[dict[str, Any]]) -> None:
        if not players:
            return
        
        try:
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cur:
                    # Upsert players
                    execute_values(
                        cur,
                        """
                        INSERT INTO players (
                            id, full_name, short_name, primary_pos, team_id, last_seen_at, headshot_url
                        ) VALUES %s
                        ON CONFLICT (id) DO UPDATE SET
                            full_name = EXCLUDED.full_name,
                            short_name = EXCLUDED.short_name,
                            primary_pos = EXCLUDED.primary_pos,
                            team_id = EXCLUDED.team_id,
                            last_seen_at = EXCLUDED.last_seen_at,
                            headshot_url = EXCLUDED.headshot_url
                        """,
                        [
                            (
                                p["id"],
                                p["full_name"],
                                p["short_name"],
                                p["primary_pos"],
                                p["team_id"],
                                p["last_seen_at"],
                                p["headshot_url"],
                            )
                            for p in players
                        ],
                    )
        except Exception as e:
            logging.getLogger("apps.ingest.store").error("failed to save players: %s", e)

    def save_leaderboard_rows(self, rows: list[Any]) -> None:
        if not rows:
            return
        try:
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cur:
                    targets = set((row.view_key, row.sort_stat, getattr(row, 'season', 2026)) for row in rows)
                    for vk, ss, season in targets:
                        cur.execute(
                            "DELETE FROM leaderboard_views WHERE view_key=%s AND sort_stat=%s AND season=%s",
                            (vk, ss, season),
                        )
                    execute_values(
                        cur,
                        """
                        INSERT INTO leaderboard_views
                            (view_key, sort_stat, season, rank, player_id, stat_value, refreshed_at)
                        VALUES %s
                        """,
                        [
                            (r.view_key, r.sort_stat, getattr(r, 'season', 2026),
                             r.rank, r.player_id, r.stat_value, r.refreshed_at)
                            for r in rows
                        ],
                    )
        except Exception as e:
            logging.getLogger("apps.ingest.store").error("failed to save leaderboard: %s", e)


def init_store(database_url: str) -> StoreContext:
    return StoreContext(database_url=database_url)


def fetch_triggered_alerts(database_url: str) -> list[dict]:
    """Return all alerts whose threshold is currently met and not fired in the last hour."""
    from psycopg2.extras import RealDictCursor
    try:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        ea.id::text AS id,
                        u.email,
                        p.full_name AS player_name,
                        ea.stat_name,
                        ea.threshold,
                        ea.direction,
                        ps.stat_value
                    FROM email_alerts ea
                    JOIN users u ON u.id = ea.user_id
                    JOIN players p ON p.id = ea.player_id
                    JOIN player_stats ps
                        ON ps.player_id = ea.player_id
                       AND ps.stat_name = ea.stat_name
                       AND ps.valid_to IS NULL
                    WHERE
                      (
                        (ea.direction = 'up'   AND ps.stat_value >= ea.threshold)
                        OR
                        (ea.direction = 'down' AND ps.stat_value <= ea.threshold)
                      )
                      AND (ea.last_fired_at IS NULL OR ea.last_fired_at < now() - interval '1 hour')
                    """,
                )
                return [dict(row) for row in cur.fetchall()]
    except Exception as exc:
        logging.getLogger("apps.ingest.store").warning("fetch_triggered_alerts failed: %s", exc)
        return []


def mark_alerts_fired(database_url: str, alert_ids: list[str]) -> None:
    """Update last_fired_at for the given alert IDs."""
    if not alert_ids:
        return
    try:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE email_alerts SET last_fired_at = now() WHERE id = ANY(%s::uuid[])",
                    (alert_ids,),
                )
    except Exception as exc:
        logging.getLogger("apps.ingest.store").warning("mark_alerts_fired failed: %s", exc)
