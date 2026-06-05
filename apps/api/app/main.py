from __future__ import annotations

import csv
import io
import json
import logging
from collections.abc import Callable

from fastapi import Body, Depends, FastAPI, HTTPException, Query, BackgroundTasks, Request
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
from .store import postgres_health_check, postgres_board_reader, postgres_player_detail_reader, postgres_player_history_reader, postgres_user_upsert, postgres_mark_premium
from .auth import make_jwt_verifier
from .users import UserUpsert, in_memory_user_upsert
from .watchlist import WatchlistLister, WatchlistAdder, WatchlistRemover
from .watchlist import in_memory_watchlist_lister, in_memory_watchlist_adder, in_memory_watchlist_remover
from .watch_boards import (
    BoardLister, BoardCreator, BoardGetter, BoardRenamer, BoardDeleter,
    BoardPlayerAdder, BoardPlayerRemover,
    in_memory_board_lister, in_memory_board_creator, in_memory_board_getter,
    in_memory_board_renamer, in_memory_board_deleter,
    in_memory_board_player_adder, in_memory_board_player_remover,
)
from .alerts import AlertLister, AlertCreator, AlertDeleter
from .alerts import in_memory_alert_lister, in_memory_alert_creator, in_memory_alert_deleter
from .creem import (
    CreemCheckout, CreemMarkPremium,
    in_memory_creem_checkout, in_memory_creem_mark_premium,
    live_creem_checkout, verify_creem_signature,
)


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
    user_upsert: UserUpsert | None = None,
    supabase_jwt_secret: str = "",
    creem_checkout: CreemCheckout | None = None,
    creem_mark_premium: CreemMarkPremium | None = None,
    creem_product_id: str = "",
    creem_webhook_secret: str = "",
    watchlist_lister: WatchlistLister | None = None,
    watchlist_adder: WatchlistAdder | None = None,
    watchlist_remover: WatchlistRemover | None = None,
    board_lister: BoardLister | None = None,
    board_creator: BoardCreator | None = None,
    board_getter: BoardGetter | None = None,
    board_renamer: BoardRenamer | None = None,
    board_deleter: BoardDeleter | None = None,
    board_player_adder: BoardPlayerAdder | None = None,
    board_player_remover: BoardPlayerRemover | None = None,
    alert_lister: AlertLister | None = None,
    alert_creator: AlertCreator | None = None,
    alert_deleter: AlertDeleter | None = None,
) -> FastAPI:
    resolved_settings = settings or load_settings()
    configure_logging(resolved_settings.log_level)

    app = FastAPI(title="diamond-departures-api")
    app.state.settings = resolved_settings
    logger = logging.getLogger("apps.api")
    checker = db_health_check or postgres_health_check(resolved_settings.database_url)
    board_loader = board_reader or postgres_board_reader(resolved_settings.database_url)
    hub = sse_hub or BoardSSEHub(heartbeat_seconds=sse_heartbeat_seconds)
    detail_loader = player_detail_reader or postgres_player_detail_reader(resolved_settings.database_url)
    history_loader = player_history_reader or postgres_player_history_reader(resolved_settings.database_url)
    season_state_loader = season_state_reader or in_memory_season_state_reader
    freshness_loader = freshness_reader or in_memory_freshness_reader
    upsert_user = user_upsert or postgres_user_upsert(resolved_settings.database_url)
    get_current_user = make_jwt_verifier(supabase_jwt_secret or resolved_settings.supabase_jwt_secret)
    checkout_fn = creem_checkout or live_creem_checkout(resolved_settings.creem_api_key)
    mark_premium_fn = creem_mark_premium or postgres_mark_premium(resolved_settings.database_url)
    effective_product_id = creem_product_id or resolved_settings.creem_product_id
    effective_webhook_secret = creem_webhook_secret or resolved_settings.creem_webhook_secret

    from .store import (
        postgres_watchlist_lister, postgres_watchlist_adder, postgres_watchlist_remover,
        postgres_board_lister, postgres_board_creator, postgres_board_getter,
        postgres_board_renamer, postgres_board_deleter,
        postgres_board_player_adder, postgres_board_player_remover,
        postgres_alert_lister, postgres_alert_creator, postgres_alert_deleter,
    )

    wl_lister  = watchlist_lister  or postgres_watchlist_lister(resolved_settings.database_url)
    wl_adder   = watchlist_adder   or postgres_watchlist_adder(resolved_settings.database_url)
    wl_remover = watchlist_remover or postgres_watchlist_remover(resolved_settings.database_url)

    b_lister     = board_lister        or postgres_board_lister(resolved_settings.database_url)
    b_creator    = board_creator       or postgres_board_creator(resolved_settings.database_url)
    b_getter     = board_getter        or postgres_board_getter(resolved_settings.database_url)
    b_renamer    = board_renamer       or postgres_board_renamer(resolved_settings.database_url)
    b_deleter    = board_deleter       or postgres_board_deleter(resolved_settings.database_url)
    b_pl_adder   = board_player_adder  or postgres_board_player_adder(resolved_settings.database_url)
    b_pl_remover = board_player_remover or postgres_board_player_remover(resolved_settings.database_url)

    a_lister  = alert_lister  or postgres_alert_lister(resolved_settings.database_url)
    a_creator = alert_creator or postgres_alert_creator(resolved_settings.database_url)
    a_deleter = alert_deleter or postgres_alert_deleter(resolved_settings.database_url)

    def _require_premium(payload: dict = Depends(get_current_user)) -> dict:
        user = upsert_user(payload["sub"], payload.get("email", ""), None, None)
        if not user.get("is_premium"):
            raise HTTPException(status_code=403, detail="Premium required")
        return payload

    app.state.sse_hub = hub

    @app.get("/api/health")
    def health() -> JSONResponse:
        db_ok = checker()
        payload = {
            "status": "ok" if db_ok else "degraded",
            "checks": {"database": "reachable" if db_ok else "unreachable"},
        }
        if not db_ok:
            logger.warning("health check degraded: database unreachable")
        return JSONResponse(status_code=200 if db_ok else 503, content=payload)

    @app.get("/api/board")
    def board(
        view: str = Query(...),
        sort: str = Query(...),
        season: int = Query(default=None),
    ) -> JSONResponse:
        _validate_view_sort(view, sort)
        effective_season = season if season is not None else resolved_settings.current_season
        rows = board_loader(view, sort, effective_season)[:100]
        return JSONResponse(content={
            "view": view,
            "sort": sort,
            "season": effective_season,
            "entries": _entries_from_rows(rows),
        })

    @app.get("/api/board/sse")
    async def board_sse(
        view: str = Query(...),
        sort: str = Query(...),
        season: int = Query(default=None),
    ) -> StreamingResponse:
        _validate_view_sort(view, sort)
        effective_season = season if season is not None else resolved_settings.current_season
        rows = board_loader(view, sort, effective_season)[:100]
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
        return JSONResponse(content={"player_id": player_id, "stat": stat, "points": sorted_history})

    @app.get("/api/season-state")
    def season_state() -> JSONResponse:
        payload = season_state_loader()
        if payload.get("mode") not in VALID_SEASON_MODES:
            raise HTTPException(status_code=500, detail="Invalid season mode")
        return JSONResponse(content=payload, headers={"Cache-Control": "public, max-age=300"})

    @app.get("/api/freshness")
    def freshness() -> JSONResponse:
        return JSONResponse(content=freshness_loader(), headers={"Cache-Control": "no-store"})

    @app.get("/api/auth/me")
    def auth_me(payload: dict = Depends(get_current_user)) -> JSONResponse:
        user_meta = payload.get("user_metadata") or {}
        name = user_meta.get("full_name") or user_meta.get("name") or payload.get("email", "").split("@")[0]
        avatar_url = user_meta.get("avatar_url") or user_meta.get("picture")
        user = upsert_user(payload["sub"], payload.get("email", ""), name, avatar_url)
        return JSONResponse(content=user)

    @app.post("/api/creem/checkout")
    def creem_checkout_endpoint(payload: dict = Depends(get_current_user)) -> JSONResponse:
        url = checkout_fn(
            effective_product_id,
            payload["sub"],
            payload.get("email", ""),
            "https://diamonddepartures.com/upgrade/success",
        )
        return JSONResponse(content={"checkout_url": url})

    @app.post("/api/creem/webhook")
    async def creem_webhook(request: Request) -> JSONResponse:
        body = await request.body()
        sig = request.headers.get("creem-signature", "")
        if effective_webhook_secret and not verify_creem_signature(body, sig, effective_webhook_secret):
            raise HTTPException(status_code=400, detail="Invalid signature")
        try:
            event = json.loads(body)
        except (json.JSONDecodeError, ValueError):
            raise HTTPException(status_code=400, detail="Invalid JSON body")
        if event.get("type") == "payment.succeeded":
            user_id = event.get("data", {}).get("metadata", {}).get("user_id", "")
            if user_id:
                mark_premium_fn(user_id)
        return JSONResponse(content={"ok": True})

    @app.get("/api/watchlist")
    def get_watchlist(payload: dict = Depends(_require_premium)) -> JSONResponse:
        return JSONResponse(content=wl_lister(payload["sub"]))

    @app.post("/api/watchlist")
    def add_watchlist(body: dict = Body(...), payload: dict = Depends(_require_premium)) -> JSONResponse:
        wl_adder(payload["sub"], int(body["player_id"]))
        return JSONResponse(content={"ok": True})

    @app.delete("/api/watchlist/{player_id}")
    def remove_watchlist(player_id: int, payload: dict = Depends(_require_premium)) -> JSONResponse:
        wl_remover(payload["sub"], player_id)
        return JSONResponse(content={"ok": True})

    @app.get("/api/watch-boards")
    def list_boards(payload: dict = Depends(_require_premium)) -> JSONResponse:
        return JSONResponse(content=b_lister(payload["sub"]))

    @app.post("/api/watch-boards")
    def create_board(body: dict = Body(...), payload: dict = Depends(_require_premium)) -> JSONResponse:
        board = b_creator(payload["sub"], str(body["name"]))
        return JSONResponse(content=board)

    @app.get("/api/watch-boards/{board_id}")
    def get_board(board_id: str, payload: dict = Depends(_require_premium)) -> JSONResponse:
        board = b_getter(board_id, payload["sub"])
        if board is None:
            raise HTTPException(status_code=404, detail="Board not found")
        return JSONResponse(content=board)

    @app.put("/api/watch-boards/{board_id}")
    def rename_board(board_id: str, body: dict = Body(...), payload: dict = Depends(_require_premium)) -> JSONResponse:
        if not b_renamer(board_id, payload["sub"], str(body["name"])):
            raise HTTPException(status_code=404, detail="Board not found")
        return JSONResponse(content={"ok": True})

    @app.delete("/api/watch-boards/{board_id}")
    def delete_board(board_id: str, payload: dict = Depends(_require_premium)) -> JSONResponse:
        b_deleter(board_id, payload["sub"])
        return JSONResponse(content={"ok": True})

    @app.post("/api/watch-boards/{board_id}/players/{player_id}")
    def add_board_player(board_id: str, player_id: int, payload: dict = Depends(_require_premium)) -> JSONResponse:
        if not b_pl_adder(board_id, payload["sub"], player_id):
            raise HTTPException(status_code=404, detail="Board not found")
        return JSONResponse(content={"ok": True})

    @app.delete("/api/watch-boards/{board_id}/players/{player_id}")
    def remove_board_player(board_id: str, player_id: int, payload: dict = Depends(_require_premium)) -> JSONResponse:
        b_pl_remover(board_id, payload["sub"], player_id)
        return JSONResponse(content={"ok": True})

    @app.get("/api/alerts")
    def list_alerts(payload: dict = Depends(_require_premium)) -> JSONResponse:
        return JSONResponse(content=a_lister(payload["sub"]))

    @app.post("/api/alerts")
    def create_alert(body: dict = Body(...), payload: dict = Depends(_require_premium)) -> JSONResponse:
        alert = a_creator(
            payload["sub"],
            int(body["player_id"]),
            str(body["stat_name"]),
            float(body["threshold"]),
            str(body["direction"]),
        )
        return JSONResponse(content=alert)

    @app.delete("/api/alerts/{alert_id}")
    def delete_alert(alert_id: str, payload: dict = Depends(_require_premium)) -> JSONResponse:
        a_deleter(alert_id, payload["sub"])
        return JSONResponse(content={"ok": True})

    @app.get("/api/board/export")
    def board_export(
        view: str = Query(...),
        sort: str = Query(...),
        season: int = Query(default=None),
        payload: dict = Depends(_require_premium),
    ) -> StreamingResponse:
        _validate_view_sort(view, sort)
        effective_season = season if season is not None else resolved_settings.current_season
        rows = board_loader(view, sort, effective_season)[:100]
        entries = _entries_from_rows(rows)

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["rank", "name", "team", "position", "stat", "stat_value"])
        for e in entries:
            writer.writerow([
                e["rank"],
                e["player"]["name"],
                e["player"]["team_abbr"],
                e["player"]["position"],
                sort,
                e["stat_value"],
            ])
        buf.seek(0)

        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=diamond-departures-{view}-{sort}.csv"},
        )

    @app.on_event("startup")
    async def start_db_poller() -> None:
        import asyncio
        asyncio.create_task(_db_poll_loop(
            hub=hub,
            board_loader=board_loader,
            current_season=resolved_settings.current_season,
            poll_seconds=resolved_settings.sse_poll_seconds,
            logger=logger,
        ))

    return app


async def _db_poll_loop(
    *,
    hub: BoardSSEHub,
    board_loader: BoardReader,
    current_season: int,
    poll_seconds: float,
    logger: logging.Logger,
) -> None:
    import asyncio
    last_seen: dict[tuple, str] = {}

    while True:
        await asyncio.sleep(poll_seconds)
        try:
            with hub._lock:
                active_keys = list(hub._connections.keys())
            for view, sort in active_keys:
                rows = board_loader(view, sort, current_season)
                if not rows:
                    continue
                ts = str(rows[0]["refreshed_at"])
                key = (view, sort)
                if last_seen.get(key) != ts:
                    last_seen[key] = ts
                    entries = _entries_from_rows(rows)
                    hub.publish_snapshot(view, sort, entries)
                    logger.debug("SSE snapshot published: %s/%s", view, sort)
        except Exception as exc:
            logger.warning("db_poll_loop error: %s", exc)


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
