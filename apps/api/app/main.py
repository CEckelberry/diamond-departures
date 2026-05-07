from __future__ import annotations

import logging
from collections.abc import Callable

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from .board import (
    VALID_SORTS,
    VALID_VIEWS,
    BoardReader,
    age_category,
    in_memory_board_reader,
    parse_refreshed_at,
)
from .config import ApiSettings, load_settings
from .logging import configure_logging
from .store import postgres_health_check


def create_app(
    settings: ApiSettings | None = None,
    db_health_check: Callable[[], bool] | None = None,
    board_reader: BoardReader | None = None,
) -> FastAPI:
    resolved_settings = settings or load_settings()
    configure_logging(resolved_settings.log_level)

    app = FastAPI(title="diamond-departures-api")
    app.state.settings = resolved_settings
    logger = logging.getLogger("apps.api")
    checker = db_health_check or postgres_health_check(resolved_settings.database_url)
    board_loader = board_reader or in_memory_board_reader

    @app.get("/api/health")
    def health() -> JSONResponse:
        db_ok = checker()
        payload = {
            "status": "ok" if db_ok else "degraded",
            "checks": {
                "database": "reachable" if db_ok else "unreachable",
            },
        }
        status_code = 200 if db_ok else 503
        if not db_ok:
            logger.warning("health check degraded: database unreachable")
        return JSONResponse(status_code=status_code, content=payload)

    @app.get("/api/board")
    def board(
        view: str = Query(...),
        sort: str = Query(...),
    ) -> JSONResponse:
        if view not in VALID_VIEWS:
            raise HTTPException(status_code=400, detail=f"Invalid view '{view}'")
        if sort not in VALID_SORTS:
            raise HTTPException(status_code=400, detail=f"Invalid sort '{sort}'")

        rows = board_loader(view, sort)[:100]
        entries: list[dict[str, object]] = []
        for row in rows:
            refreshed_at = parse_refreshed_at(str(row["refreshed_at"]))
            entries.append(
                {
                    "rank": row["rank"],
                    "player": {
                        "id": row["player_id"],
                        "name": row["player_name"],
                        "team_abbr": row["team_abbr"],
                        "headshot_url": row["headshot_url"],
                        "position": row["position"],
                    },
                    "stat_value": row["stat_value"],
                    "freshness": {
                        "timestamp": refreshed_at.isoformat(),
                        "age_category": age_category(refreshed_at),
                    },
                }
            )

        return JSONResponse(
            content={
                "view": view,
                "sort": sort,
                "entries": entries,
            }
        )

    return app
