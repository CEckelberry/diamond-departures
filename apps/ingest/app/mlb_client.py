from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Callable
from urllib.error import HTTPError
from urllib.request import urlopen


@dataclass(frozen=True)
class MLBResponse:
    status_code: int
    payload: dict
    headers: dict[str, str]


class MLBApiClient:
    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: int = 10,
        max_retries: int = 3,
        retry_backoff_seconds: float = 1.0,
        request_fn: Callable[[str, int], object] | None = None,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.retry_backoff_seconds = retry_backoff_seconds
        self.request_fn = request_fn or self._default_request
        self.sleep_fn = sleep_fn or time.sleep

    def _default_request(self, url: str, timeout: int) -> MLBResponse:
        try:
            with urlopen(url, timeout=timeout) as response:  # nosec B310
                body = response.read().decode("utf-8")
                parsed = json.loads(body) if body else {}
                headers = {k: v for k, v in response.headers.items()}
                return MLBResponse(status_code=response.status, payload=parsed, headers=headers)
        except HTTPError as exc:
            body = exc.read().decode("utf-8") if exc.fp else ""
            parsed = json.loads(body) if body else {}
            headers = {k: v for k, v in (exc.headers.items() if exc.headers else [])}
            return MLBResponse(status_code=exc.code, payload=parsed, headers=headers)

    def get_json(self, path: str) -> MLBResponse:
        url = f"{self.base_url}/{path.lstrip('/')}"
        attempts = self.max_retries + 1

        for index in range(attempts):
            response = self.request_fn(url, self.timeout_seconds)
            if isinstance(response, MLBResponse):
                normalized = response
            else:
                normalized = MLBResponse(
                    status_code=response.status_code,
                    payload=response.payload,
                    headers=response.headers or {},
                )

            if normalized.status_code < 400:
                return normalized

            retryable = normalized.status_code == 429 or normalized.status_code >= 500
            if not retryable or index == attempts - 1:
                raise RuntimeError(f"MLB API request failed: status={normalized.status_code} url={url}")

            if normalized.status_code == 429:
                wait = float(normalized.headers.get("Retry-After", self.retry_backoff_seconds))
            else:
                wait = self.retry_backoff_seconds * (index + 1)
            self.sleep_fn(wait)

        raise RuntimeError(f"MLB API request failed: status=unknown url={url}")
