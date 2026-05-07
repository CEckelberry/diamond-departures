from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable

InvalidateCallback = Callable[[str, str, str], None]


@dataclass(frozen=True)
class RefreshTarget:
    view: str
    sort: str


@dataclass
class PubSubMessage:
    payload: dict[str, Any]
    ack: Callable[[], None]
    nack: Callable[[], None]


class RefreshSubscriber:
    def __init__(self, *, invalidate: InvalidateCallback, logger: logging.Logger | None = None) -> None:
        self._invalidate = invalidate
        self._logger = logger or logging.getLogger("apps.api.pubsub")

    def process(self, message: PubSubMessage) -> None:
        reason = str(message.payload.get("reason", "ingest"))
        targets = _extract_targets(message.payload)
        try:
            for target in targets:
                self._invalidate(target.view, target.sort, reason)
                self._logger.info(
                    "refreshed view=%s sort=%s reason=%s",
                    target.view,
                    target.sort,
                    reason,
                )
            message.ack()
        except Exception:
            message.nack()
            raise


def _extract_targets(payload: dict[str, Any]) -> list[RefreshTarget]:
    if "views" in payload:
        views = payload.get("views")
        if not isinstance(views, list):
            raise ValueError("'views' must be a list")
        targets: list[RefreshTarget] = []
        for item in views:
            if not isinstance(item, dict):
                raise ValueError("each 'views' item must be an object")
            targets.append(_parse_target(item))
        return targets

    return [_parse_target(payload)]


def _parse_target(raw: dict[str, Any]) -> RefreshTarget:
    view = raw.get("view")
    sort = raw.get("sort")
    if not isinstance(view, str) or not isinstance(sort, str):
        raise ValueError("message must include string 'view' and 'sort'")
    return RefreshTarget(view=view, sort=sort)
