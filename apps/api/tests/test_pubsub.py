from __future__ import annotations

import logging

import pytest

from apps.api.app.pubsub import PubSubMessage, RefreshSubscriber


def _message(payload: dict[str, object]) -> tuple[PubSubMessage, dict[str, int]]:
    state = {"ack": 0, "nack": 0}
    msg = PubSubMessage(
        payload=payload,
        ack=lambda: state.__setitem__("ack", state["ack"] + 1),
        nack=lambda: state.__setitem__("nack", state["nack"] + 1),
    )
    return msg, state


def test_subscriber_invalidates_each_target_key() -> None:
    refreshed: list[tuple[str, str, str]] = []
    subscriber = RefreshSubscriber(
        invalidate=lambda view, sort, reason: refreshed.append((view, sort, reason)),
    )
    message, _state = _message(
        {
            "reason": "ingest-tick",
            "views": [
                {"view": "hitters", "sort": "wRC+"},
                {"view": "pitchers", "sort": "ERA"},
            ],
        }
    )

    subscriber.process(message)

    assert refreshed == [
        ("hitters", "wRC+", "ingest-tick"),
        ("pitchers", "ERA", "ingest-tick"),
    ]


def test_subscriber_acks_on_success() -> None:
    subscriber = RefreshSubscriber(invalidate=lambda _v, _s, _r: None)
    message, state = _message({"view": "hitters", "sort": "wRC+"})

    subscriber.process(message)

    assert state == {"ack": 1, "nack": 0}


def test_subscriber_nacks_on_invalidation_error() -> None:
    def _boom(_view: str, _sort: str, _reason: str) -> None:
        raise RuntimeError("boom")

    subscriber = RefreshSubscriber(invalidate=_boom)
    message, state = _message({"view": "hitters", "sort": "wRC+"})

    with pytest.raises(RuntimeError, match="boom"):
        subscriber.process(message)

    assert state == {"ack": 0, "nack": 1}


def test_subscriber_logs_refresh_context(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)
    subscriber = RefreshSubscriber(invalidate=lambda _v, _s, _r: None)
    message, _state = _message(
        {"reason": "ingest", "views": [{"view": "hitters", "sort": "OPS"}]}
    )

    subscriber.process(message)

    assert "refreshed view=hitters sort=OPS reason=ingest" in caplog.text
