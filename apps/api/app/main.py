from __future__ import annotations

import logging
from collections.abc import Callable

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
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
from .store import postgres_health_check, postgres_board_reader, postgres_player_detail_reader, postgres_player_history_reader


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
    
    # Use postgres_board_reader if database_url is provided, otherwise fallback to in-memory
    board_loader = board_reader or postgres_board_reader(resolved_settings.database_url)
    
    hub = sse_hub or BoardSSEHub(heartbeat_seconds=sse_heartbeat_seconds)
    detail_loader = player_detail_reader or postgres_player_detail_reader(resolved_settings.database_url)
    history_loader = player_history_reader or postgres_player_history_reader(resolved_settings.database_url)
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
                "stat_value": float(row["stat_value"]),
                "additional_stats": {k: float(v) for k, v in row.get("additional_stats", {}).items()},
                "freshness": {
                    "timestamp": refreshed_at.isoformat(),
                    "age_category": age_category(refreshed_at),
                },
            }
        )

    return entries


app = create_app()

import asyncio
import random
from datetime import datetime, timezone

async def simulation_loop():
    """Background task to nudge stats and trigger flips."""
    hub = app.state.sse_hub
    settings = app.state.settings
    
    while True:
        await asyncio.sleep(8) # Flip every 8 seconds
        
        # Identify active connections to simulate relevant views
        active_keys = []
        with hub._lock:
            active_keys = list(hub._connections.keys())
            
        if not active_keys:
            continue
            
        
        for view, sort in active_keys:
            # 1. Get current rows for this view
            from .store import postgres_board_reader
            reader = postgres_board_reader(settings.database_url)
            rows = reader(view, sort)
            if not rows:
                continue
                
            # 2. Pick a random player to nudge
            idx = random.randint(0, min(10, len(rows)-1))
            player = rows[idx]
            
            # 3. Nudge the value (very slight change)
            old_val = float(player['stat_value'])
            is_reverse = sort in ['ERA', 'FIP', 'WHIP', 'E']
            change = random.uniform(0.01, 0.05) if sort not in ['wRC+', 'HR', 'RBI', 'K', 'W', 'SB', 'OAA', 'E', 'PO', 'A', 'DP', 'Def', 'UZR'] else float(random.randint(1, 2))
            
            if random.random() > 0.5:
                new_val = old_val + change
            else:
                new_val = old_val - change
                
            player['stat_value'] = new_val
            player['refreshed_at'] = datetime.now(timezone.utc).isoformat()
            
            # 4. Publish the update
            entries = _entries_from_rows(rows)
            hub.publish_snapshot(view, sort, entries)


@app.on_event("startup")
async def start_simulation():
    asyncio.create_task(simulation_loop())

