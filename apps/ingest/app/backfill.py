"""One-time CLI to backfill season stats for 2016 through last year.

Usage:
    python -m apps.ingest.app.backfill
    python -m apps.ingest.app.backfill --start-year 2020 --end-year 2023
    python -m apps.ingest.app.backfill --dry-run

Skips any year that already has player_stats rows for that season.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import UTC, datetime

import psycopg2
from psycopg2.extras import RealDictCursor

from .config import load_settings
from .season_stats import SeasonStatsRefresher

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("backfill")


def _season_has_data(database_url: str, season: int) -> bool:
    try:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT 1 FROM player_stats WHERE season = %s LIMIT 1",
                    (season,),
                )
                return cur.fetchone() is not None
    except Exception as exc:
        log.warning("Could not check season %d: %s", season, exc)
        return False


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Backfill historical season stats")
    parser.add_argument("--start-year", type=int, default=2016)
    parser.add_argument("--end-year",   type=int, default=datetime.now(UTC).year - 1)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    settings = load_settings()
    refresher = SeasonStatsRefresher(
        database_url=settings.database_url,
        mlb_api_url=settings.mlb_api_url,
    )

    years = list(range(args.start_year, args.end_year + 1))
    log.info("Backfill plan: %s", years)

    for year in years:
        if _season_has_data(settings.database_url, year):
            log.info("Season %d already has data — skipping", year)
            continue
        if args.dry_run:
            log.info("[dry-run] Would refresh season %d", year)
            continue
        log.info("Refreshing season %d ...", year)
        result = refresher.refresh(season=year)
        log.info(
            "Season %d done: players=%d stats=%d errors=%s",
            year, result.players_upserted, result.stats_upserted, result.errors,
        )
        time.sleep(2)

    log.info("Backfill complete.")


if __name__ == "__main__":
    main()
