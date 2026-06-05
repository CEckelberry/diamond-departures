from __future__ import annotations

import hashlib
import hmac
from collections.abc import Callable

import httpx


CreemCheckout = Callable[[str, str, str, str], str]
CreemMarkPremium = Callable[[str], None]


def in_memory_creem_checkout(product_id: str, user_id: str, email: str, success_url: str) -> str:
    return "https://creem.io/demo-checkout"


def in_memory_creem_mark_premium(user_id: str) -> None:
    pass


def live_creem_checkout(api_key: str, product_id: str) -> CreemCheckout:
    def _checkout(prod_id: str, user_id: str, email: str, success_url: str) -> str:
        resp = httpx.post(
            "https://api.creem.io/v1/checkouts",
            headers={"x-api-key": api_key},
            json={
                "product_id": prod_id,
                "success_url": success_url,
                "metadata": {"user_id": user_id, "email": email},
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["checkout_url"]
    return _checkout


def verify_creem_signature(body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
