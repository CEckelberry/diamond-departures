from __future__ import annotations

import logging
from collections.abc import Callable

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse

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
from .players import (
    VALID_HISTORY_STATS,
    PlayerDetailReader,
    PlayerHistoryReader,
    in_memory_player_detail_reader,
    in_memory_player_history_reader,
)
from .sse import BoardSSEHub
from .status import (
    VALID_SEASON_MODES,
    FreshnessReader,
    SeasonStateReader,
    in_memory_freshness_reader,
    in_memory_season_state_reader,
)
from .store import postgres_health_check


def create_app(
    settings: ApiSettings | None = None,
    db_health_check: Callable[[], bool] | None = None,
    board_reader: BoardReader | None = None,
    sse_hub: BoardSSEHub | None = None,
    sse_heartbeat_seconds: float = 30.0,
    player_detail_reader: PlayerDetailReader | None = None,
    player_history_reader: PlayerHistoryReader | None = None,
    season_state_reader: SeasonStateReader | None = None,
    freshness_reader: FreshnessReader | None = None,
) -> FastAPI:
    resolved_settings = settings or load_settings()
    configure_logging(resolved_settings.log_level)

    app = FastAPI(title="diamond-departures-api")
    app.state.settings = resolved_settings
    logger = logging.getLogger("apps.api")
    checker = db_health_check or postgres_health_check(resolved_settings.database_url)
    board_loader = board_reader or in_memory_board_reader
    hub = sse_hub or BoardSSEHub(heartbeat_seconds=sse_heartbeat_seconds)
    detail_loader = player_detail_reader or in_memory_player_detail_reader
    history_loader = player_history_reader or in_memory_player_history_reader
    season_state_loader = season_state_reader or in_memory_season_state_reader
    freshness_loader = freshness_reader or in_memory_freshness_reader
    app.state.sse_hub = hub

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
        _validate_view_sort(view, sort)
        rows = board_loader(view, sort)[:100]
        return JSONResponse(
            content={
                "view": view,
                "sort": sort,
                "entries": _entries_from_rows(rows),
            }
        )

    @app.get("/api/board/sse")
    async def board_sse(
        view: str = Query(...),
        sort: str = Query(...),
    ) -> StreamingResponse:
        _validate_view_sort(view, sort)
        rows = board_loader(view, sort)[:100]

        return StreamingResponse(
            hub.stream(view, sort, _entries_from_rows(rows)),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @app.get("/api/players/{player_id}")
    def player_detail(player_id: int) -> JSONResponse:
        detail = detail_loader(player_id)
        if detail is None:
            raise HTTPException(status_code=404, detail=f"Player '{player_id}' not found")
        return JSONResponse(content=detail)

    @app.get("/api/players/{player_id}/history")
    def player_history(player_id: int, stat: str | None = Query(default=None)) -> JSONResponse:
        if stat is None or stat not in VALID_HISTORY_STATS:
            raise HTTPException(status_code=400, detail="Invalid stat")

        history = history_loader(player_id, stat)
        if history is None:
            raise HTTPException(status_code=404, detail=f"Player '{player_id}' not found")

        sorted_history = sorted(history, key=lambda row: str(row["timestamp"]))
        return JSONResponse(
            content={
                "player_id": player_id,
                "stat": stat,
                "points": sorted_history,
            }
        )

    @app.get("/api/season-state")
    def season_state() -> JSONResponse:
        payload = season_state_loader()
        if payload.get("mode") not in VALID_SEASON_MODES:
            raise HTTPException(status_code=500, detail="Invalid season mode")
        return JSONResponse(
            content=payload,
            headers={"Cache-Control": "public, max-age=300"},
        )

    @app.get("/api/freshness")
    def freshness() -> JSONResponse:
        return JSONResponse(
            content=freshness_loader(),
            headers={"Cache-Control": "no-store"},
        )

    return app


def _validate_view_sort(view: str, sort: str) -> None:
    if view not in VALID_VIEWS:
        raise HTTPException(status_code=400, detail=f"Invalid view '{view}'")
    if sort not in VALID_SORTS:
        raise HTTPException(status_code=400, detail=f"Invalid sort '{sort}'")


def _entries_from_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
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
    return entries
