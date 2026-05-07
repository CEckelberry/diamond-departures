from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Callable


def _shape(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _shape(value[key]) for key in sorted(value.keys())}
    if isinstance(value, list):
        if not value:
            return ["empty"]
        child_shapes = sorted({_normalize_for_sort(_shape(item)) for item in value})
        return [child_shapes]
    return type(value).__name__


def _normalize_for_sort(value: Any) -> str:
    return repr(value)


def shape_hash(payload: dict[str, Any]) -> str:
    canonical = repr(_shape(payload)).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


@dataclass(frozen=True)
class DriftResult:
    source: str
    signature: str
    drifted: bool
    parse_error: bool


class DriftDetector:
    def __init__(
        self,
        *,
        signatures: dict[str, str] | None = None,
        log_fn: Callable[[str, str], None] | None = None,
    ) -> None:
        self._signatures = signatures or {}
        self._log_fn = log_fn or (lambda *_args, **_kwargs: None)

    def evaluate(
        self,
        *,
        source: str,
        payload: dict[str, Any],
        required_paths: list[str] | None = None,
    ) -> DriftResult:
        required_paths = required_paths or []
        signature = shape_hash(payload)
        previous = self._signatures.get(source)
        drifted = previous is not None and previous != signature

        parse_error = False
        for path in required_paths:
            if not self._has_path(payload, path):
                parse_error = True
                self._log_fn("ERROR", f"schema parse failure for {source}: missing {path}")

        if drifted:
            self._log_fn("WARN", f"schema drift detected for {source}")

        self._signatures[source] = signature
        return DriftResult(
            source=source,
            signature=signature,
            drifted=drifted,
            parse_error=parse_error,
        )

    def _has_path(self, payload: dict[str, Any], path: str) -> bool:
        current: Any = payload
        for key in path.split("."):
            if isinstance(current, dict) and key in current:
                current = current[key]
                continue
            return False
        return True
