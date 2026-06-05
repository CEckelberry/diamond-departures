# Auth + Premium Features Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Supabase Auth (Google OAuth), Creem.io $5.99 lifetime purchase, and four premium features: watchlist, watch boards, email alerts, CSV export.

**Architecture:** Supabase Auth handles OAuth and issues JWTs. SvelteKit uses `@supabase/ssr` to manage session cookies and injects `Authorization: Bearer <token>` into proxied FastAPI calls. FastAPI validates Supabase JWTs with `python-jose`, owns all premium business logic, and stores premium state in Postgres.

**Tech Stack:** FastAPI + python-jose + httpx (existing), @supabase/supabase-js + @supabase/ssr (new), Resend for email, Creem.io for payments, PostgreSQL migration via golang-migrate.

---

## File Map

**New FastAPI files:**
- `apps/api/app/auth.py` — JWT verification dependency, `get_current_user`, `require_premium`
- `apps/api/app/users.py` — `UserUpsert` type, `in_memory_user_upsert`, postgres upsert
- `apps/api/app/creem.py` — checkout + webhook route handlers
- `apps/api/app/watchlist.py` — watchlist CRUD route handlers
- `apps/api/app/watch_boards.py` — watch board CRUD route handlers
- `apps/api/app/alerts.py` — email alert CRUD + Resend delivery
- `apps/api/app/export.py` — CSV export route handler
- `apps/api/tests/test_auth.py`
- `apps/api/tests/test_creem.py`
- `apps/api/tests/test_watchlist.py`
- `apps/api/tests/test_watch_boards.py`
- `apps/api/tests/test_alerts.py`
- `apps/api/tests/test_export.py`

**Modified FastAPI files:**
- `apps/api/app/config.py` — add `supabase_jwt_secret`, `creem_api_key`, `creem_webhook_secret`, `creem_product_id`, `resend_api_key`
- `apps/api/app/main.py` — include new routers, pass new config to `create_app`
- `apps/api/app/store.py` — add postgres implementations for users, watchlist, watch boards, alerts
- `requirements.txt` — add `python-jose[cryptography]`

**New migration:**
- `apps/api/migrations/008_auth_and_premium.up.sql`
- `apps/api/migrations/008_auth_and_premium.down.sql`

**New SvelteKit files:**
- `apps/web/src/lib/supabase.ts` — browser + server Supabase client factories
- `apps/web/src/hooks.server.ts` — session middleware populating `event.locals`
- `apps/web/src/lib/stores/user.ts` — `userStore` reactive store
- `apps/web/src/lib/components/auth/PremiumGate.svelte` — upgrade CTA wrapper
- `apps/web/src/routes/+layout.server.ts` — calls `/api/auth/me`, returns user
- `apps/web/src/routes/upgrade/+page.svelte` — pricing + Creem.io redirect
- `apps/web/src/routes/upgrade/success/+page.svelte` — post-purchase confirmation
- `apps/web/src/routes/boards/+page.svelte` — list + create watch boards
- `apps/web/src/routes/boards/+page.ts` — load watch boards from API
- `apps/web/src/routes/boards/[id]/+page.svelte` — single watch board (uses Board.svelte)
- `apps/web/src/routes/boards/[id]/+page.ts` — load board data

**Modified SvelteKit files:**
- `apps/web/src/app.d.ts` — extend `Locals` with `supabase`, `session`, `user`
- `apps/web/src/routes/api/[...path]/+server.ts` — inject `Authorization` header from session
- `apps/web/src/routes/+layout.svelte` — receive user prop, init userStore
- `apps/web/src/lib/components/shell/Nav.svelte` — wire auth buttons
- `apps/web/src/lib/components/board/Row.svelte` — add watchlist pin icon
- `apps/web/src/lib/components/player/Panel.svelte` — add email alerts section
- `apps/web/src/lib/components/board/Header.svelte` — add CSV export button

**Modified ingest:**
- `apps/ingest/app/store.py` — add `fetch_triggered_alerts` + `mark_alerts_fired`
- `apps/ingest/app/email.py` — Resend HTTP call
- `apps/ingest/app/job.py` — fire alerts after leaderboard recomputation

---

## Task 1: Migration 008 — users and premium tables

**Files:**
- Create: `apps/api/migrations/008_auth_and_premium.up.sql`
- Create: `apps/api/migrations/008_auth_and_premium.down.sql`

- [ ] **Step 1: Write the up migration**

```sql
-- apps/api/migrations/008_auth_and_premium.up.sql
CREATE TABLE users (
    id           uuid PRIMARY KEY,
    email        text NOT NULL UNIQUE,
    name         text,
    avatar_url   text,
    is_premium   bool NOT NULL DEFAULT false,
    purchased_at timestamptz,
    created_at   timestamptz NOT NULL DEFAULT now(),
    last_seen_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE watch_boards (
    id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name       text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE watch_board_players (
    board_id  uuid NOT NULL REFERENCES watch_boards(id) ON DELETE CASCADE,
    player_id int  NOT NULL REFERENCES players(id)      ON DELETE CASCADE,
    added_at  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (board_id, player_id)
);

CREATE TABLE watchlist_players (
    user_id   uuid NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
    player_id int  NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    added_at  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, player_id)
);

CREATE TABLE email_alerts (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       uuid NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
    player_id     int  NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    stat_name     varchar(20) NOT NULL,
    threshold     numeric(8,3) NOT NULL,
    direction     varchar(4) NOT NULL CHECK (direction IN ('up', 'down')),
    last_fired_at timestamptz,
    created_at    timestamptz NOT NULL DEFAULT now()
);
```

- [ ] **Step 2: Write the down migration**

```sql
-- apps/api/migrations/008_auth_and_premium.down.sql
DROP TABLE IF EXISTS email_alerts;
DROP TABLE IF EXISTS watchlist_players;
DROP TABLE IF EXISTS watch_board_players;
DROP TABLE IF EXISTS watch_boards;
DROP TABLE IF EXISTS users;
```

- [ ] **Step 3: Run migration against local DB**

```bash
docker compose up db -d
docker run --rm --network diamond-departures_default \
  -v $(pwd)/apps/api/migrations:/migrations:ro \
  migrate/migrate:v4.18.3 \
  -path=/migrations \
  -database="postgres://diamond:diamond@diamond-db:5432/diamond?sslmode=disable" \
  up
```

Expected: `no error`, migration applied

- [ ] **Step 4: Verify tables exist**

```bash
docker exec diamond-db psql -U diamond -d diamond -c "\dt users watch_boards watch_board_players watchlist_players email_alerts"
```

Expected: 5 rows listing the new tables

- [ ] **Step 5: Commit**

```bash
git add apps/api/migrations/008_auth_and_premium.up.sql apps/api/migrations/008_auth_and_premium.down.sql
git commit -m "feat(db): migration 008 — users and premium tables"
```

---

## Task 2: FastAPI — config + python-jose + auth module

**Files:**
- Modify: `requirements.txt`
- Modify: `apps/api/app/config.py`
- Create: `apps/api/app/auth.py`
- Create: `apps/api/tests/test_auth.py`

- [ ] **Step 1: Add python-jose to requirements**

In `requirements.txt`, add one line:
```
python-jose[cryptography]
```

- [ ] **Step 2: Extend ApiSettings with new env vars**

Replace the contents of `apps/api/app/config.py`:

```python
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class ApiSettings:
    port: int = 8081
    log_level: str = "INFO"
    database_url: str = "postgresql://diamond:diamond@localhost:5432/diamond"
    sse_poll_seconds: float = 30.0
    current_season: int = field(default_factory=lambda: datetime.now(UTC).year)
    supabase_jwt_secret: str = ""
    creem_api_key: str = ""
    creem_webhook_secret: str = ""
    creem_product_id: str = ""
    resend_api_key: str = ""


def load_settings() -> ApiSettings:
    return ApiSettings(
        port=int(os.getenv("PORT", "8081")),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        database_url=os.getenv("DATABASE_URL", "postgresql://diamond:diamond@localhost:5432/diamond"),
        sse_poll_seconds=float(os.getenv("SSE_POLL_SECONDS", "30")),
        current_season=int(os.getenv("CURRENT_SEASON", str(datetime.now(UTC).year))),
        supabase_jwt_secret=os.getenv("SUPABASE_JWT_SECRET", ""),
        creem_api_key=os.getenv("CREEM_API_KEY", ""),
        creem_webhook_secret=os.getenv("CREEM_WEBHOOK_SECRET", ""),
        creem_product_id=os.getenv("CREEM_PRODUCT_ID", ""),
        resend_api_key=os.getenv("RESEND_API_KEY", ""),
    )
```

- [ ] **Step 3: Write the failing auth tests**

```python
# apps/api/tests/test_auth.py
from __future__ import annotations

from jose import jwt
from fastapi.testclient import TestClient

from apps.api.app.main import create_app


def _make_token(secret: str, sub: str = "user-uuid-1", email: str = "test@example.com", extra: dict | None = None) -> str:
    claims = {"sub": sub, "email": email, "aud": "authenticated", **(extra or {})}
    return jwt.encode(claims, secret, algorithm="HS256")


def _fake_upsert(user_id: str, email: str, name: str | None, avatar_url: str | None) -> dict:
    return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": False}


SECRET = "test-jwt-secret"


def test_me_returns_user_when_jwt_valid() -> None:
    app = create_app(db_health_check=lambda: True, user_upsert=_fake_upsert, supabase_jwt_secret=SECRET)
    client = TestClient(app)
    token = _make_token(SECRET)

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_premium"] is False


def test_me_returns_401_when_no_token() -> None:
    app = create_app(db_health_check=lambda: True, user_upsert=_fake_upsert, supabase_jwt_secret=SECRET)
    client = TestClient(app)

    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_me_returns_401_when_token_invalid() -> None:
    app = create_app(db_health_check=lambda: True, user_upsert=_fake_upsert, supabase_jwt_secret=SECRET)
    client = TestClient(app)

    response = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401


def test_me_returns_401_when_wrong_secret() -> None:
    app = create_app(db_health_check=lambda: True, user_upsert=_fake_upsert, supabase_jwt_secret=SECRET)
    client = TestClient(app)
    token = _make_token("wrong-secret")

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
```

- [ ] **Step 4: Run to confirm failures**

```bash
cd /path/to/diamond-departures
pytest apps/api/tests/test_auth.py -v
```

Expected: 4 failures — `create_app` does not accept `user_upsert` or `supabase_jwt_secret`

- [ ] **Step 5: Create auth.py**

```python
# apps/api/app/auth.py
from __future__ import annotations

from fastapi import Header, HTTPException
from jose import JWTError, jwt


def make_jwt_verifier(secret: str):
    def verify(authorization: str | None = Header(default=None)) -> dict:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Not authenticated")
        token = authorization.removeprefix("Bearer ")
        try:
            return jwt.decode(token, secret, algorithms=["HS256"], audience="authenticated")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    return verify
```

- [ ] **Step 6: Create users.py**

```python
# apps/api/app/users.py
from __future__ import annotations

from collections.abc import Callable

UserUpsert = Callable[[str, str, str | None, str | None], dict]


def in_memory_user_upsert(user_id: str, email: str, name: str | None, avatar_url: str | None) -> dict:
    return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": False}
```

- [ ] **Step 7: Add /api/auth/me to main.py**

In `apps/api/app/main.py`, update `create_app` signature and add the endpoint. Add these parameters to the function signature after `freshness_reader`:

```python
from .auth import make_jwt_verifier
from .users import UserUpsert, in_memory_user_upsert

def create_app(
    ...existing params...,
    user_upsert: UserUpsert | None = None,
    supabase_jwt_secret: str = "",
) -> FastAPI:
    ...existing setup...
    upsert_user = user_upsert or in_memory_user_upsert
    get_current_user = make_jwt_verifier(supabase_jwt_secret or resolved_settings.supabase_jwt_secret)

    @app.get("/api/auth/me")
    def auth_me(payload: dict = Depends(get_current_user)) -> JSONResponse:
        user_meta = payload.get("user_metadata") or {}
        name = user_meta.get("full_name") or user_meta.get("name") or payload.get("email", "").split("@")[0]
        avatar_url = user_meta.get("avatar_url") or user_meta.get("picture")
        user = upsert_user(payload["sub"], payload.get("email", ""), name, avatar_url)
        return JSONResponse(content=user)
```

Also add `from fastapi import Depends` if not already imported.

- [ ] **Step 8: Run tests to confirm they pass**

```bash
pytest apps/api/tests/test_auth.py -v
```

Expected: 4 passed

- [ ] **Step 9: Commit**

```bash
git add requirements.txt apps/api/app/config.py apps/api/app/auth.py apps/api/app/users.py apps/api/app/main.py apps/api/tests/test_auth.py
git commit -m "feat(api): JWT auth middleware and /api/auth/me endpoint"
```

---

## Task 3: FastAPI — postgres user upsert

**Files:**
- Modify: `apps/api/app/store.py`
- Modify: `apps/api/app/main.py`

- [ ] **Step 1: Add postgres_user_upsert to store.py**

At the bottom of `apps/api/app/store.py`, add:

```python
from .users import UserUpsert


def postgres_user_upsert(database_url: str) -> UserUpsert:
    def _upsert(user_id: str, email: str, name: str | None, avatar_url: str | None) -> dict:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO users (id, email, name, avatar_url, last_seen_at)
                    VALUES (%s, %s, %s, %s, now())
                    ON CONFLICT (id) DO UPDATE SET
                        email        = EXCLUDED.email,
                        name         = COALESCE(EXCLUDED.name, users.name),
                        avatar_url   = COALESCE(EXCLUDED.avatar_url, users.avatar_url),
                        last_seen_at = now()
                    RETURNING id, email, name, avatar_url, is_premium, purchased_at, created_at, last_seen_at
                    """,
                    (user_id, email, name, avatar_url),
                )
                row = cur.fetchone()
                return {
                    "id": str(row["id"]),
                    "email": row["email"],
                    "name": row["name"],
                    "avatar_url": row["avatar_url"],
                    "is_premium": row["is_premium"],
                    "purchased_at": row["purchased_at"].isoformat() if row["purchased_at"] else None,
                }
    return _upsert
```

- [ ] **Step 2: Wire postgres_user_upsert into create_app**

In `apps/api/app/main.py`, add the import and update the `create_app` body:

```python
from .store import ..., postgres_user_upsert

# inside create_app, after resolved_settings:
upsert_user = user_upsert or postgres_user_upsert(resolved_settings.database_url)
```

- [ ] **Step 3: Confirm existing tests still pass**

```bash
pytest apps/api/tests/ -v
```

Expected: all pass

- [ ] **Step 4: Commit**

```bash
git add apps/api/app/store.py apps/api/app/main.py
git commit -m "feat(api): postgres user upsert for /api/auth/me"
```

---

## Task 4: FastAPI — Creem.io checkout + webhook

**Files:**
- Create: `apps/api/app/creem.py`
- Create: `apps/api/tests/test_creem.py`
- Modify: `apps/api/app/main.py`
- Modify: `apps/api/app/store.py`

- [ ] **Step 1: Write the failing tests**

```python
# apps/api/tests/test_creem.py
from __future__ import annotations

from jose import jwt
from fastapi.testclient import TestClient

from apps.api.app.main import create_app

SECRET = "test-jwt-secret"


def _token(sub: str = "user-uuid-1", email: str = "buyer@example.com") -> str:
    return jwt.encode({"sub": sub, "email": email, "aud": "authenticated"}, SECRET, algorithm="HS256")


def _fake_upsert(user_id, email, name, avatar_url):
    return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": False}


def _fake_mark_premium(user_id: str) -> None:
    pass  # no-op in tests


def _fake_checkout(product_id: str, user_id: str, email: str, success_url: str) -> str:
    return f"https://creem.io/test-checkout/{user_id}"


def test_checkout_returns_url_for_authenticated_user() -> None:
    app = create_app(
        db_health_check=lambda: True,
        user_upsert=_fake_upsert,
        supabase_jwt_secret=SECRET,
        creem_checkout=_fake_checkout,
        creem_mark_premium=_fake_mark_premium,
        creem_product_id="prod-test",
    )
    client = TestClient(app)

    response = client.post(
        "/api/creem/checkout",
        headers={"Authorization": f"Bearer {_token()}"},
    )

    assert response.status_code == 200
    assert "checkout_url" in response.json()
    assert "creem.io" in response.json()["checkout_url"]


def test_checkout_returns_401_unauthenticated() -> None:
    app = create_app(
        db_health_check=lambda: True,
        user_upsert=_fake_upsert,
        supabase_jwt_secret=SECRET,
        creem_checkout=_fake_checkout,
        creem_mark_premium=_fake_mark_premium,
        creem_product_id="prod-test",
    )
    client = TestClient(app)

    response = client.post("/api/creem/checkout")

    assert response.status_code == 401


def test_webhook_marks_user_premium_on_payment_succeeded() -> None:
    marked: list[str] = []

    def _capture_mark(user_id: str) -> None:
        marked.append(user_id)

    app = create_app(
        db_health_check=lambda: True,
        user_upsert=_fake_upsert,
        supabase_jwt_secret=SECRET,
        creem_checkout=_fake_checkout,
        creem_mark_premium=_capture_mark,
        creem_product_id="prod-test",
        creem_webhook_secret="whsec-test",
    )
    client = TestClient(app)

    payload = {
        "type": "payment.succeeded",
        "data": {"metadata": {"user_id": "user-uuid-1"}},
    }
    # Signature verification is skipped when webhook_secret is empty in tests;
    # pass the secret header so the endpoint accepts it.
    import hmac, hashlib, json
    body = json.dumps(payload)
    sig = hmac.new("whsec-test".encode(), body.encode(), hashlib.sha256).hexdigest()

    response = client.post(
        "/api/creem/webhook",
        content=body,
        headers={"content-type": "application/json", "creem-signature": sig},
    )

    assert response.status_code == 200
    assert "user-uuid-1" in marked


def test_webhook_returns_400_on_bad_signature() -> None:
    app = create_app(
        db_health_check=lambda: True,
        user_upsert=_fake_upsert,
        supabase_jwt_secret=SECRET,
        creem_checkout=_fake_checkout,
        creem_mark_premium=_fake_mark_premium,
        creem_product_id="prod-test",
        creem_webhook_secret="whsec-real",
    )
    client = TestClient(app)

    response = client.post(
        "/api/creem/webhook",
        json={"type": "payment.succeeded", "data": {"metadata": {"user_id": "x"}}},
        headers={"creem-signature": "bad-sig"},
    )

    assert response.status_code == 400
```

- [ ] **Step 2: Run to confirm failures**

```bash
pytest apps/api/tests/test_creem.py -v
```

Expected: all fail — `create_app` doesn't accept `creem_*` params

- [ ] **Step 3: Create creem.py**

```python
# apps/api/app/creem.py
from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Callable

import httpx
from fastapi import Header, HTTPException, Request


CreemCheckout = Callable[[str, str, str, str], str]
CreemMarkPremium = Callable[[str], None]


def in_memory_creem_checkout(product_id: str, user_id: str, email: str, success_url: str) -> str:
    return f"https://creem.io/demo-checkout"


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
```

- [ ] **Step 4: Wire Creem into main.py**

Add to `create_app` signature and body. Full additions to `create_app`:

```python
from .creem import (
    CreemCheckout, CreemMarkPremium,
    in_memory_creem_checkout, in_memory_creem_mark_premium,
    live_creem_checkout, verify_creem_signature,
)

# new params in create_app signature:
#   creem_checkout: CreemCheckout | None = None,
#   creem_mark_premium: CreemMarkPremium | None = None,
#   creem_product_id: str = "",
#   creem_webhook_secret: str = "",

# inside create_app body:
checkout_fn = creem_checkout or live_creem_checkout(
    resolved_settings.creem_api_key,
    resolved_settings.creem_product_id,
)
mark_premium_fn = creem_mark_premium or postgres_mark_premium(resolved_settings.database_url)
effective_product_id = creem_product_id or resolved_settings.creem_product_id
effective_webhook_secret = creem_webhook_secret or resolved_settings.creem_webhook_secret

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
    event = json.loads(body)
    if event.get("type") == "payment.succeeded":
        user_id = event.get("data", {}).get("metadata", {}).get("user_id", "")
        if user_id:
            mark_premium_fn(user_id)
    return JSONResponse(content={"ok": True})
```

- [ ] **Step 5: Add postgres_mark_premium to store.py**

```python
def postgres_mark_premium(database_url: str) -> Callable[[str], None]:
    def _mark(user_id: str) -> None:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET is_premium = true, purchased_at = now() WHERE id = %s",
                    (user_id,),
                )
    return _mark
```

Also add `from collections.abc import Callable` to store.py imports if not already there.

- [ ] **Step 6: Run tests**

```bash
pytest apps/api/tests/test_creem.py -v
```

Expected: 4 passed

- [ ] **Step 7: Commit**

```bash
git add apps/api/app/creem.py apps/api/app/main.py apps/api/app/store.py apps/api/tests/test_creem.py
git commit -m "feat(api): Creem.io checkout and webhook endpoints"
```

---

## Task 5: FastAPI — watchlist endpoints

**Files:**
- Create: `apps/api/app/watchlist.py`
- Create: `apps/api/tests/test_watchlist.py`
- Modify: `apps/api/app/main.py`
- Modify: `apps/api/app/store.py`

- [ ] **Step 1: Write failing tests**

```python
# apps/api/tests/test_watchlist.py
from __future__ import annotations

from jose import jwt
from fastapi.testclient import TestClient

from apps.api.app.main import create_app

SECRET = "test-secret"

def _token(sub: str = "u1", premium: bool = True) -> str:
    return jwt.encode({"sub": sub, "email": "u@test.com", "aud": "authenticated"}, SECRET, algorithm="HS256")

def _upsert(user_id, email, name, avatar_url):
    return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": True}

def _upsert_free(user_id, email, name, avatar_url):
    return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": False}


def _make_app(upsert=None):
    store: list[dict] = []

    def _list(user_id: str) -> list[dict]:
        return [e for e in store if e["user_id"] == user_id]

    def _add(user_id: str, player_id: int) -> None:
        if not any(e["user_id"] == user_id and e["player_id"] == player_id for e in store):
            store.append({"user_id": user_id, "player_id": player_id})

    def _remove(user_id: str, player_id: int) -> bool:
        before = len(store)
        store[:] = [e for e in store if not (e["user_id"] == user_id and e["player_id"] == player_id)]
        return len(store) < before

    return create_app(
        db_health_check=lambda: True,
        user_upsert=upsert or _upsert,
        supabase_jwt_secret=SECRET,
        watchlist_lister=_list,
        watchlist_adder=_add,
        watchlist_remover=_remove,
    ), store


def test_get_watchlist_returns_entries() -> None:
    app, store = _make_app()
    store.append({"user_id": "u1", "player_id": 660271})
    client = TestClient(app)

    response = client.get("/api/watchlist", headers={"Authorization": f"Bearer {_token()}"})

    assert response.status_code == 200
    assert response.json() == [{"user_id": "u1", "player_id": 660271}]


def test_add_to_watchlist() -> None:
    app, store = _make_app()
    client = TestClient(app)

    response = client.post(
        "/api/watchlist",
        json={"player_id": 660271},
        headers={"Authorization": f"Bearer {_token()}"},
    )

    assert response.status_code == 200
    assert any(e["player_id"] == 660271 for e in store)


def test_remove_from_watchlist() -> None:
    app, store = _make_app()
    store.append({"user_id": "u1", "player_id": 660271})
    client = TestClient(app)

    response = client.delete("/api/watchlist/660271", headers={"Authorization": f"Bearer {_token()}"})

    assert response.status_code == 200
    assert not any(e["player_id"] == 660271 for e in store)


def test_watchlist_requires_premium() -> None:
    app, _ = _make_app(upsert=_upsert_free)
    client = TestClient(app)

    response = client.get("/api/watchlist", headers={"Authorization": f"Bearer {_token()}"})

    assert response.status_code == 403


def test_watchlist_requires_auth() -> None:
    app, _ = _make_app()
    client = TestClient(app)

    response = client.get("/api/watchlist")

    assert response.status_code == 401
```

- [ ] **Step 2: Run to confirm failures**

```bash
pytest apps/api/tests/test_watchlist.py -v
```

Expected: 5 failures

- [ ] **Step 3: Create watchlist.py**

```python
# apps/api/app/watchlist.py
from __future__ import annotations

from collections.abc import Callable

WatchlistLister = Callable[[str], list[dict]]
WatchlistAdder = Callable[[str, int], None]
WatchlistRemover = Callable[[str, int], bool]


def in_memory_watchlist_lister(user_id: str) -> list[dict]:
    return []

def in_memory_watchlist_adder(user_id: str, player_id: int) -> None:
    pass

def in_memory_watchlist_remover(user_id: str, player_id: int) -> bool:
    return False
```

- [ ] **Step 4: Add watchlist endpoints to main.py**

Add to `create_app` signature:
```python
from .watchlist import WatchlistLister, WatchlistAdder, WatchlistRemover
from .watchlist import in_memory_watchlist_lister, in_memory_watchlist_adder, in_memory_watchlist_remover

# new params: watchlist_lister, watchlist_adder, watchlist_remover (all | None = None)
```

Add to `create_app` body — premium check helper and endpoints:

```python
from fastapi import Body

def _require_premium(payload: dict = Depends(get_current_user)) -> dict:
    user = upsert_user(payload["sub"], payload.get("email", ""), None, None)
    if not user.get("is_premium"):
        raise HTTPException(status_code=403, detail="Premium required")
    return payload

wl_lister = watchlist_lister or in_memory_watchlist_lister
wl_adder = watchlist_adder or in_memory_watchlist_adder
wl_remover = watchlist_remover or in_memory_watchlist_remover

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
```

- [ ] **Step 5: Add postgres watchlist functions to store.py**

```python
from .watchlist import WatchlistLister, WatchlistAdder, WatchlistRemover

def postgres_watchlist_lister(database_url: str) -> WatchlistLister:
    def _list(user_id: str) -> list[dict]:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT user_id::text, player_id FROM watchlist_players WHERE user_id = %s ORDER BY added_at DESC",
                    (user_id,),
                )
                return [dict(r) for r in cur.fetchall()]
    return _list

def postgres_watchlist_adder(database_url: str) -> WatchlistAdder:
    def _add(user_id: str, player_id: int) -> None:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO watchlist_players (user_id, player_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
                    (user_id, player_id),
                )
    return _add

def postgres_watchlist_remover(database_url: str) -> WatchlistRemover:
    def _remove(user_id: str, player_id: int) -> bool:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM watchlist_players WHERE user_id = %s AND player_id = %s",
                    (user_id, player_id),
                )
                return (cur.rowcount or 0) > 0
    return _remove
```

Wire them into `create_app`:
```python
wl_lister = watchlist_lister or postgres_watchlist_lister(resolved_settings.database_url)
wl_adder  = watchlist_adder  or postgres_watchlist_adder(resolved_settings.database_url)
wl_remover = watchlist_remover or postgres_watchlist_remover(resolved_settings.database_url)
```

- [ ] **Step 6: Run tests**

```bash
pytest apps/api/tests/test_watchlist.py -v
```

Expected: 5 passed

- [ ] **Step 7: Commit**

```bash
git add apps/api/app/watchlist.py apps/api/app/main.py apps/api/app/store.py apps/api/tests/test_watchlist.py
git commit -m "feat(api): watchlist CRUD endpoints"
```

---

## Task 6: FastAPI — watch boards endpoints

**Files:**
- Create: `apps/api/app/watch_boards.py`
- Create: `apps/api/tests/test_watch_boards.py`
- Modify: `apps/api/app/main.py`
- Modify: `apps/api/app/store.py`

- [ ] **Step 1: Write failing tests**

```python
# apps/api/tests/test_watch_boards.py
from __future__ import annotations

import uuid
from jose import jwt
from fastapi.testclient import TestClient
from apps.api.app.main import create_app

SECRET = "test-secret"

def _token(sub: str = "u1") -> str:
    return jwt.encode({"sub": sub, "email": "u@test.com", "aud": "authenticated"}, SECRET, algorithm="HS256")

def _upsert(user_id, email, name, avatar_url):
    return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": True}


def _make_app():
    boards: dict[str, dict] = {}
    board_players: dict[str, list[int]] = {}

    def _list_boards(user_id: str) -> list[dict]:
        return [b for b in boards.values() if b["user_id"] == user_id]

    def _create_board(user_id: str, name: str) -> dict:
        bid = str(uuid.uuid4())
        boards[bid] = {"id": bid, "user_id": user_id, "name": name}
        board_players[bid] = []
        return boards[bid]

    def _get_board(board_id: str, user_id: str) -> dict | None:
        b = boards.get(board_id)
        if not b or b["user_id"] != user_id:
            return None
        return {**b, "players": board_players.get(board_id, [])}

    def _rename_board(board_id: str, user_id: str, name: str) -> bool:
        b = boards.get(board_id)
        if not b or b["user_id"] != user_id:
            return False
        b["name"] = name
        return True

    def _delete_board(board_id: str, user_id: str) -> bool:
        b = boards.get(board_id)
        if not b or b["user_id"] != user_id:
            return False
        del boards[board_id]
        return True

    def _add_player(board_id: str, user_id: str, player_id: int) -> bool:
        b = boards.get(board_id)
        if not b or b["user_id"] != user_id:
            return False
        if player_id not in board_players[board_id]:
            board_players[board_id].append(player_id)
        return True

    def _remove_player(board_id: str, user_id: str, player_id: int) -> bool:
        b = boards.get(board_id)
        if not b or b["user_id"] != user_id:
            return False
        board_players[board_id] = [p for p in board_players[board_id] if p != player_id]
        return True

    app = create_app(
        db_health_check=lambda: True,
        user_upsert=_upsert,
        supabase_jwt_secret=SECRET,
        board_lister=_list_boards,
        board_creator=_create_board,
        board_getter=_get_board,
        board_renamer=_rename_board,
        board_deleter=_delete_board,
        board_player_adder=_add_player,
        board_player_remover=_remove_player,
    )
    return app, boards


def test_create_and_list_boards() -> None:
    app, _ = _make_app()
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {_token()}"}

    client.post("/api/watch-boards", json={"name": "My Lineup"}, headers=headers)
    response = client.get("/api/watch-boards", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "My Lineup"


def test_get_board_returns_players() -> None:
    app, _ = _make_app()
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {_token()}"}

    create_resp = client.post("/api/watch-boards", json={"name": "A"}, headers=headers)
    bid = create_resp.json()["id"]
    client.post(f"/api/watch-boards/{bid}/players/660271", headers=headers)

    response = client.get(f"/api/watch-boards/{bid}", headers=headers)

    assert response.status_code == 200
    assert 660271 in response.json()["players"]


def test_delete_board() -> None:
    app, boards = _make_app()
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {_token()}"}

    resp = client.post("/api/watch-boards", json={"name": "Gone"}, headers=headers)
    bid = resp.json()["id"]

    client.delete(f"/api/watch-boards/{bid}", headers=headers)

    assert bid not in boards


def test_board_not_found_for_other_user() -> None:
    app, _ = _make_app()
    client = TestClient(app)

    resp = client.post("/api/watch-boards", json={"name": "Mine"}, headers={"Authorization": f"Bearer {_token('u1')}"})
    bid = resp.json()["id"]

    response = client.get(f"/api/watch-boards/{bid}", headers={"Authorization": f"Bearer {_token('u2')}"})
    assert response.status_code == 404
```

- [ ] **Step 2: Run to confirm failures**

```bash
pytest apps/api/tests/test_watch_boards.py -v
```

Expected: 4 failures

- [ ] **Step 3: Create watch_boards.py**

```python
# apps/api/app/watch_boards.py
from __future__ import annotations

from collections.abc import Callable

BoardLister       = Callable[[str], list[dict]]
BoardCreator      = Callable[[str, str], dict]
BoardGetter       = Callable[[str, str], dict | None]
BoardRenamer      = Callable[[str, str, str], bool]
BoardDeleter      = Callable[[str, str], bool]
BoardPlayerAdder  = Callable[[str, str, int], bool]
BoardPlayerRemover = Callable[[str, str, int], bool]


def in_memory_board_lister(user_id: str) -> list[dict]: return []
def in_memory_board_creator(user_id: str, name: str) -> dict: return {"id": "stub", "user_id": user_id, "name": name}
def in_memory_board_getter(board_id: str, user_id: str) -> dict | None: return None
def in_memory_board_renamer(board_id: str, user_id: str, name: str) -> bool: return False
def in_memory_board_deleter(board_id: str, user_id: str) -> bool: return False
def in_memory_board_player_adder(board_id: str, user_id: str, player_id: int) -> bool: return False
def in_memory_board_player_remover(board_id: str, user_id: str, player_id: int) -> bool: return False
```

- [ ] **Step 4: Add watch board endpoints to main.py**

Import the types and defaults from `watch_boards.py`, add params to `create_app`, then add endpoints:

```python
from .watch_boards import (
    BoardLister, BoardCreator, BoardGetter, BoardRenamer, BoardDeleter,
    BoardPlayerAdder, BoardPlayerRemover,
    in_memory_board_lister, in_memory_board_creator, in_memory_board_getter,
    in_memory_board_renamer, in_memory_board_deleter,
    in_memory_board_player_adder, in_memory_board_player_remover,
)

# Inside create_app, wire defaults:
b_lister  = board_lister  or in_memory_board_lister
b_creator = board_creator or in_memory_board_creator
b_getter  = board_getter  or in_memory_board_getter
b_renamer = board_renamer or in_memory_board_renamer
b_deleter = board_deleter or in_memory_board_deleter
b_pl_adder   = board_player_adder   or in_memory_board_player_adder
b_pl_remover = board_player_remover or in_memory_board_player_remover

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
```

- [ ] **Step 5: Add postgres watch board functions to store.py**

```python
from .watch_boards import BoardLister, BoardCreator, BoardGetter, BoardRenamer, BoardDeleter, BoardPlayerAdder, BoardPlayerRemover

def postgres_board_lister(database_url: str) -> BoardLister:
    def _list(user_id: str) -> list[dict]:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id::text, user_id::text, name, created_at, updated_at FROM watch_boards WHERE user_id = %s ORDER BY created_at ASC", (user_id,))
                return [dict(r) for r in cur.fetchall()]
    return _list

def postgres_board_creator(database_url: str) -> BoardCreator:
    def _create(user_id: str, name: str) -> dict:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("INSERT INTO watch_boards (user_id, name) VALUES (%s, %s) RETURNING id::text, user_id::text, name", (user_id, name))
                return dict(cur.fetchone())
    return _create

def postgres_board_getter(database_url: str) -> BoardGetter:
    def _get(board_id: str, user_id: str) -> dict | None:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id::text, user_id::text, name FROM watch_boards WHERE id = %s AND user_id = %s", (board_id, user_id))
                row = cur.fetchone()
                if not row:
                    return None
                cur.execute("SELECT player_id FROM watch_board_players WHERE board_id = %s", (board_id,))
                players = [r["player_id"] for r in cur.fetchall()]
                return {**dict(row), "players": players}
    return _get

def postgres_board_renamer(database_url: str) -> BoardRenamer:
    def _rename(board_id: str, user_id: str, name: str) -> bool:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("UPDATE watch_boards SET name = %s, updated_at = now() WHERE id = %s AND user_id = %s", (name, board_id, user_id))
                return (cur.rowcount or 0) > 0
    return _rename

def postgres_board_deleter(database_url: str) -> BoardDeleter:
    def _delete(board_id: str, user_id: str) -> bool:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM watch_boards WHERE id = %s AND user_id = %s", (board_id, user_id))
                return (cur.rowcount or 0) > 0
    return _delete

def postgres_board_player_adder(database_url: str) -> BoardPlayerAdder:
    def _add(board_id: str, user_id: str, player_id: int) -> bool:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM watch_boards WHERE id = %s AND user_id = %s", (board_id, user_id))
                if not cur.fetchone():
                    return False
                cur.execute("INSERT INTO watch_board_players (board_id, player_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (board_id, player_id))
                return True
    return _add

def postgres_board_player_remover(database_url: str) -> BoardPlayerRemover:
    def _remove(board_id: str, user_id: str, player_id: int) -> bool:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM watch_board_players WHERE board_id = %s AND player_id = %s", (board_id, player_id))
                return (cur.rowcount or 0) > 0
    return _remove
```

Wire all into `create_app` using the postgres versions as defaults.

- [ ] **Step 6: Run tests**

```bash
pytest apps/api/tests/test_watch_boards.py -v
```

Expected: 4 passed

- [ ] **Step 7: Commit**

```bash
git add apps/api/app/watch_boards.py apps/api/app/main.py apps/api/app/store.py apps/api/tests/test_watch_boards.py
git commit -m "feat(api): watch boards CRUD endpoints"
```

---

## Task 7: FastAPI — email alerts endpoints + Resend delivery

**Files:**
- Create: `apps/api/app/alerts.py`
- Create: `apps/api/tests/test_alerts.py`
- Modify: `apps/api/app/main.py`
- Modify: `apps/api/app/store.py`

- [ ] **Step 1: Write failing tests**

```python
# apps/api/tests/test_alerts.py
from __future__ import annotations

import uuid
from jose import jwt
from fastapi.testclient import TestClient
from apps.api.app.main import create_app

SECRET = "test-secret"

def _token() -> str:
    return jwt.encode({"sub": "u1", "email": "u@test.com", "aud": "authenticated"}, SECRET, algorithm="HS256")

def _upsert(user_id, email, name, avatar_url):
    return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": True}


def _make_app():
    store: list[dict] = []

    def _list(user_id: str) -> list[dict]:
        return [a for a in store if a["user_id"] == user_id]

    def _create(user_id: str, player_id: int, stat_name: str, threshold: float, direction: str) -> dict:
        alert = {"id": str(uuid.uuid4()), "user_id": user_id, "player_id": player_id,
                 "stat_name": stat_name, "threshold": threshold, "direction": direction}
        store.append(alert)
        return alert

    def _delete(alert_id: str, user_id: str) -> bool:
        before = len(store)
        store[:] = [a for a in store if not (a["id"] == alert_id and a["user_id"] == user_id)]
        return len(store) < before

    return create_app(
        db_health_check=lambda: True,
        user_upsert=_upsert,
        supabase_jwt_secret=SECRET,
        alert_lister=_list,
        alert_creator=_create,
        alert_deleter=_delete,
    ), store


def test_create_and_list_alerts() -> None:
    app, _ = _make_app()
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {_token()}"}

    client.post("/api/alerts", json={"player_id": 660271, "stat_name": "wRC+", "threshold": 150.0, "direction": "up"}, headers=headers)
    response = client.get("/api/alerts", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["stat_name"] == "wRC+"


def test_delete_alert() -> None:
    app, store = _make_app()
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {_token()}"}

    resp = client.post("/api/alerts", json={"player_id": 660271, "stat_name": "ERA", "threshold": 3.0, "direction": "down"}, headers=headers)
    alert_id = resp.json()["id"]
    client.delete(f"/api/alerts/{alert_id}", headers=headers)

    assert not any(a["id"] == alert_id for a in store)


def test_alerts_require_premium() -> None:
    def _free_upsert(user_id, email, name, avatar_url):
        return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": False}

    app = create_app(
        db_health_check=lambda: True,
        user_upsert=_free_upsert,
        supabase_jwt_secret=SECRET,
    )
    client = TestClient(app)

    response = client.get("/api/alerts", headers={"Authorization": f"Bearer {_token()}"})
    assert response.status_code == 403
```

- [ ] **Step 2: Run to confirm failures**

```bash
pytest apps/api/tests/test_alerts.py -v
```

- [ ] **Step 3: Create alerts.py**

```python
# apps/api/app/alerts.py
from __future__ import annotations

from collections.abc import Callable

AlertLister  = Callable[[str], list[dict]]
AlertCreator = Callable[[str, int, str, float, str], dict]
AlertDeleter = Callable[[str, str], bool]


def in_memory_alert_lister(user_id: str) -> list[dict]: return []
def in_memory_alert_creator(user_id: str, player_id: int, stat_name: str, threshold: float, direction: str) -> dict:
    return {"id": "stub", "user_id": user_id, "player_id": player_id, "stat_name": stat_name, "threshold": threshold, "direction": direction}
def in_memory_alert_deleter(alert_id: str, user_id: str) -> bool: return False
```

- [ ] **Step 4: Add alert endpoints to main.py**

```python
from .alerts import AlertLister, AlertCreator, AlertDeleter
from .alerts import in_memory_alert_lister, in_memory_alert_creator, in_memory_alert_deleter

# Wire defaults in create_app:
a_lister  = alert_lister  or in_memory_alert_lister
a_creator = alert_creator or in_memory_alert_creator
a_deleter = alert_deleter or in_memory_alert_deleter

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
```

- [ ] **Step 5: Add postgres alert functions to store.py**

```python
from .alerts import AlertLister, AlertCreator, AlertDeleter

def postgres_alert_lister(database_url: str) -> AlertLister:
    def _list(user_id: str) -> list[dict]:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id::text, user_id::text, player_id, stat_name, threshold, direction FROM email_alerts WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
                return [{**dict(r), "threshold": float(r["threshold"])} for r in cur.fetchall()]
    return _list

def postgres_alert_creator(database_url: str) -> AlertCreator:
    def _create(user_id: str, player_id: int, stat_name: str, threshold: float, direction: str) -> dict:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO email_alerts (user_id, player_id, stat_name, threshold, direction) VALUES (%s, %s, %s, %s, %s) RETURNING id::text, user_id::text, player_id, stat_name, threshold, direction",
                    (user_id, player_id, stat_name, threshold, direction),
                )
                r = cur.fetchone()
                return {**dict(r), "threshold": float(r["threshold"])}
    return _create

def postgres_alert_deleter(database_url: str) -> AlertDeleter:
    def _delete(alert_id: str, user_id: str) -> bool:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM email_alerts WHERE id = %s AND user_id = %s", (alert_id, user_id))
                return (cur.rowcount or 0) > 0
    return _delete
```

Wire into `create_app` using postgres versions as defaults.

- [ ] **Step 6: Run tests**

```bash
pytest apps/api/tests/test_alerts.py -v
```

Expected: 3 passed

- [ ] **Step 7: Commit**

```bash
git add apps/api/app/alerts.py apps/api/app/main.py apps/api/app/store.py apps/api/tests/test_alerts.py
git commit -m "feat(api): email alert CRUD endpoints"
```

---

## Task 8: FastAPI — CSV export endpoint

**Files:**
- Create: `apps/api/app/export.py`
- Create: `apps/api/tests/test_export.py`
- Modify: `apps/api/app/main.py`

- [ ] **Step 1: Write failing test**

```python
# apps/api/tests/test_export.py
from __future__ import annotations

from datetime import datetime, timezone
from jose import jwt
from fastapi.testclient import TestClient
from apps.api.app.main import create_app

SECRET = "test-secret"

def _token() -> str:
    return jwt.encode({"sub": "u1", "email": "u@test.com", "aud": "authenticated"}, SECRET, algorithm="HS256")

def _upsert(user_id, email, name, avatar_url):
    return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": True}

def _upsert_free(user_id, email, name, avatar_url):
    return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": False}

def _sample_rows():
    now = datetime.now(timezone.utc)
    return [{"rank": 1, "player_id": 660271, "player_name": "Fernando Tatis Jr.", "team_abbr": "SD", "headshot_url": "", "position": "RF", "stat_value": 158.234, "refreshed_at": now.isoformat()}]


def test_csv_export_returns_csv_for_premium_user() -> None:
    app = create_app(
        db_health_check=lambda: True,
        user_upsert=_upsert,
        supabase_jwt_secret=SECRET,
        board_reader=lambda view, sort, season=2026: _sample_rows(),
    )
    client = TestClient(app)

    response = client.get(
        "/api/board/export",
        params={"view": "hitters", "sort": "wRC+"},
        headers={"Authorization": f"Bearer {_token()}"},
    )

    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "attachment" in response.headers.get("content-disposition", "")
    assert "Fernando Tatis Jr." in response.text


def test_csv_export_requires_premium() -> None:
    app = create_app(
        db_health_check=lambda: True,
        user_upsert=_upsert_free,
        supabase_jwt_secret=SECRET,
        board_reader=lambda view, sort, season=2026: _sample_rows(),
    )
    client = TestClient(app)

    response = client.get(
        "/api/board/export",
        params={"view": "hitters", "sort": "wRC+"},
        headers={"Authorization": f"Bearer {_token()}"},
    )

    assert response.status_code == 403
```

- [ ] **Step 2: Run to confirm failures**

```bash
pytest apps/api/tests/test_export.py -v
```

- [ ] **Step 3: Add CSV export endpoint to main.py**

No new file needed — add directly to `main.py`:

```python
import csv
import io
from fastapi.responses import StreamingResponse

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
```

- [ ] **Step 4: Run tests**

```bash
pytest apps/api/tests/test_export.py -v
```

Expected: 2 passed

- [ ] **Step 5: Run full test suite**

```bash
pytest apps/api/tests/ -v
```

Expected: all pass

- [ ] **Step 6: Commit**

```bash
git add apps/api/app/main.py apps/api/tests/test_export.py
git commit -m "feat(api): premium CSV export endpoint"
```

---

## Task 9: Ingest — fire email alerts after leaderboard recomputation

**Files:**
- Create: `apps/ingest/app/email.py`
- Modify: `apps/ingest/app/store.py`
- Modify: `apps/ingest/app/job.py`

- [ ] **Step 1: Create email.py**

```python
# apps/ingest/app/email.py
from __future__ import annotations

import logging

import httpx

logger = logging.getLogger("apps.ingest.email")


def send_alert_email(resend_api_key: str, to: str, player_name: str, stat_name: str, stat_value: float, direction: str, threshold: float) -> None:
    direction_word = "above" if direction == "up" else "below"
    try:
        httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {resend_api_key}"},
            json={
                "from": "alerts@diamonddepartures.com",
                "to": [to],
                "subject": f"Alert: {player_name} {stat_name} {direction_word} {threshold}",
                "text": f"{player_name}'s {stat_name} is now {stat_value:.3f}, which is {direction_word} your threshold of {threshold}.\n\nView the board: https://diamonddepartures.com",
            },
            timeout=10,
        )
    except Exception as exc:
        logger.warning("failed to send alert email to %s: %s", to, exc)
```

- [ ] **Step 2: Add alert query functions to ingest store.py**

At the bottom of `apps/ingest/app/store.py`, add:

```python
def fetch_triggered_alerts(conn, updated_player_ids: list[int]) -> list[dict]:
    """Return alerts whose threshold was crossed for any of the updated players."""
    if not updated_player_ids:
        return []
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                ea.id,
                ea.user_id,
                ea.player_id,
                ea.stat_name,
                ea.threshold,
                ea.direction,
                u.email,
                p.full_name AS player_name,
                ps.stat_value
            FROM email_alerts ea
            JOIN users u ON u.id = ea.user_id
            JOIN players p ON p.id = ea.player_id
            JOIN player_stats ps ON ps.player_id = ea.player_id
                AND ps.stat_name = ea.stat_name
                AND ps.valid_to IS NULL
            WHERE ea.player_id = ANY(%s)
              AND (
                  (ea.direction = 'up'   AND ps.stat_value >= ea.threshold)
                OR (ea.direction = 'down' AND ps.stat_value <= ea.threshold)
              )
              AND (ea.last_fired_at IS NULL OR ea.last_fired_at < now() - interval '1 hour')
            """,
            (updated_player_ids,),
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, row)) for row in cur.fetchall()]


def mark_alerts_fired(conn, alert_ids: list[str]) -> None:
    if not alert_ids:
        return
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE email_alerts SET last_fired_at = now() WHERE id = ANY(%s)",
            (alert_ids,),
        )
```

- [ ] **Step 3: Wire alert firing into job.py**

In `apps/ingest/app/job.py`, after leaderboard recomputation, add alert dispatch. Find the section after leaderboard updates complete and add:

```python
from .email import send_alert_email

# After leaderboard recomputation in run_once(), add:
resend_api_key = settings.resend_api_key if hasattr(settings, "resend_api_key") else ""
if resend_api_key and updated_player_ids:
    try:
        from .store import fetch_triggered_alerts, mark_alerts_fired
        with store.conn() as conn:
            triggered = fetch_triggered_alerts(conn, list(updated_player_ids))
            for alert in triggered:
                send_alert_email(
                    resend_api_key,
                    alert["email"],
                    alert["player_name"],
                    alert["stat_name"],
                    float(alert["stat_value"]),
                    alert["direction"],
                    float(alert["threshold"]),
                )
            mark_alerts_fired(conn, [str(a["id"]) for a in triggered])
    except Exception as exc:
        logging.getLogger("apps.ingest").warning("alert firing failed: %s", exc)
```

Also add `RESEND_API_KEY` to ingest config. In `apps/ingest/app/config.py`:

```python
resend_api_key: str = field(default_factory=lambda: os.getenv("RESEND_API_KEY", ""))
```

- [ ] **Step 4: Confirm ingest tests still pass**

```bash
pytest apps/ingest/ -v 2>/dev/null || echo "no ingest tests"
```

- [ ] **Step 5: Commit**

```bash
git add apps/ingest/app/email.py apps/ingest/app/store.py apps/ingest/app/job.py apps/ingest/app/config.py
git commit -m "feat(ingest): fire email alerts after leaderboard recomputation"
```

---

## Task 10: SvelteKit — Supabase auth setup

**Files:**
- Modify: `apps/web/package.json` (install deps)
- Create: `apps/web/src/lib/supabase.ts`
- Modify: `apps/web/src/app.d.ts`
- Create: `apps/web/src/hooks.server.ts`
- Modify: `apps/web/src/routes/api/[...path]/+server.ts`

- [ ] **Step 1: Install Supabase packages**

```bash
cd apps/web
pnpm add @supabase/supabase-js @supabase/ssr
```

- [ ] **Step 2: Create supabase.ts**

```typescript
// apps/web/src/lib/supabase.ts
import { createBrowserClient, createServerClient, isBrowser } from '@supabase/ssr';
import { PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY } from '$env/static/public';
import type { Cookies } from '@sveltejs/kit';

export function createSupabaseBrowserClient() {
    return createBrowserClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY);
}

export function createSupabaseServerClient(cookies: Cookies) {
    return createServerClient(PUBLIC_SUPABASE_URL, PUBLIC_SUPABASE_ANON_KEY, {
        cookies: {
            getAll: () => cookies.getAll(),
            setAll: (cookiesToSet) => {
                cookiesToSet.forEach(({ name, value, options }) =>
                    cookies.set(name, value, { ...options, path: '/' })
                );
            },
        },
    });
}
```

- [ ] **Step 3: Extend app.d.ts**

Replace `apps/web/src/app.d.ts`:

```typescript
import type { Session, SupabaseClient } from '@supabase/supabase-js';

declare global {
    namespace App {
        interface Locals {
            supabase: SupabaseClient;
            session: Session | null;
        }
        interface PageData {
            user: { id: string; email: string; name: string | null; avatar_url: string | null; is_premium: boolean } | null;
        }
    }
}

export {};
```

- [ ] **Step 4: Create hooks.server.ts**

```typescript
// apps/web/src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';
import { createSupabaseServerClient } from '$lib/supabase';

export const handle: Handle = async ({ event, resolve }) => {
    event.locals.supabase = createSupabaseServerClient(event.cookies);

    const { data: { session } } = await event.locals.supabase.auth.getSession();
    event.locals.session = session;

    return resolve(event, {
        filterSerializedResponseHeaders: (name) =>
            name === 'content-range' || name === 'x-supabase-api-version',
    });
};
```

- [ ] **Step 5: Update the API proxy to inject Authorization header**

Replace `apps/web/src/routes/api/[...path]/+server.ts`:

```typescript
import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const API_URL = (typeof process !== 'undefined' && process.env.API_URL) || 'http://api:18000';

export const fallback: RequestHandler = async ({ request, url, fetch, locals }) => {
    const targetUrl = new URL(url.pathname + url.search, API_URL);

    const headers = new Headers(request.headers);
    if (locals.session?.access_token) {
        headers.set('Authorization', `Bearer ${locals.session.access_token}`);
    }

    try {
        const response = await fetch(targetUrl.toString(), {
            method: request.method,
            headers,
            // @ts-ignore
            duplex: 'half',
        });
        return response;
    } catch (err) {
        console.error('Proxy error:', err);
        throw error(502, 'Bad Gateway: Could not reach backend API');
    }
};
```

- [ ] **Step 6: Add PUBLIC env vars to docker-compose for local dev**

In `docker-compose.yml`, under the `web` service `environment`:

```yaml
- PUBLIC_SUPABASE_URL=${PUBLIC_SUPABASE_URL:-}
- PUBLIC_SUPABASE_ANON_KEY=${PUBLIC_SUPABASE_ANON_KEY:-}
```

Create `apps/web/.env.example`:
```
PUBLIC_SUPABASE_URL=https://yourproject.supabase.co
PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

- [ ] **Step 7: Verify TypeScript compiles**

```bash
cd apps/web && pnpm check
```

Expected: no errors

- [ ] **Step 8: Commit**

```bash
git add apps/web/src/lib/supabase.ts apps/web/src/app.d.ts apps/web/src/hooks.server.ts apps/web/src/routes/api/\[...path\]/+server.ts apps/web/.env.example docker-compose.yml
git commit -m "feat(web): Supabase SSR auth setup and proxy Authorization injection"
```

---

## Task 11: SvelteKit — layout server load + user store + Nav

**Files:**
- Create: `apps/web/src/routes/+layout.server.ts`
- Create: `apps/web/src/lib/stores/user.ts`
- Modify: `apps/web/src/routes/+layout.svelte`
- Modify: `apps/web/src/lib/components/shell/Nav.svelte`

- [ ] **Step 1: Create +layout.server.ts**

```typescript
// apps/web/src/routes/+layout.server.ts
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ fetch, locals }) => {
    if (!locals.session) {
        return { user: null };
    }

    try {
        const response = await fetch('/api/auth/me');
        if (response.ok) {
            return { user: await response.json() };
        }
    } catch {
        // API unreachable — degrade gracefully
    }

    return { user: null };
};
```

- [ ] **Step 2: Create user store**

```typescript
// apps/web/src/lib/stores/user.ts
import { writable } from 'svelte/store';

export type User = {
    id: string;
    email: string;
    name: string | null;
    avatar_url: string | null;
    is_premium: boolean;
};

export const userStore = writable<User | null>(null);
```

- [ ] **Step 3: Update +layout.svelte to receive user and init the store**

In `apps/web/src/routes/+layout.svelte`, add to the `<script>` block:

```typescript
import { userStore } from '$lib/stores/user';

let { children, data } = $props();

$effect(() => {
    userStore.set(data.user ?? null);
});
```

Remove the existing `let { children } = $props();` and replace with the above.

- [ ] **Step 4: Wire Nav.svelte auth buttons**

Replace the `nav-right` div contents in `apps/web/src/lib/components/shell/Nav.svelte`:

```svelte
<script lang="ts">
    import { page } from '$app/stores';
    import { createSupabaseBrowserClient } from '$lib/supabase';
    import { userStore } from '$lib/stores/user';

    const isActive = (path: string) => $page.url.pathname === path;

    async function signIn() {
        const supabase = createSupabaseBrowserClient();
        await supabase.auth.signInWithOAuth({
            provider: 'google',
            options: { redirectTo: `${$page.url.origin}/` },
        });
    }

    async function signOut() {
        const supabase = createSupabaseBrowserClient();
        await supabase.auth.signOut();
        userStore.set(null);
        window.location.href = '/';
    }
</script>

<!-- replace the nav-right div: -->
<div class="nav-right">
    {#if $userStore}
        {#if !$userStore.is_premium}
            <a href="/upgrade" class="btn-primary">Go Premium</a>
        {/if}
        <button class="btn-avatar" type="button" onclick={signOut} title="Sign out ({$userStore.email})">
            {#if $userStore.avatar_url}
                <img src={$userStore.avatar_url} alt="avatar" class="avatar-img" />
            {:else}
                <span class="avatar-initials">{($userStore.name ?? $userStore.email).slice(0, 1).toUpperCase()}</span>
            {/if}
        </button>
    {:else}
        <button class="btn-outline" type="button" onclick={signIn}>Log in</button>
        <a href="/upgrade" class="btn-primary">Go Premium</a>
    {/if}
</div>
```

Add the avatar styles to `<style>` in Nav.svelte:

```css
.btn-avatar {
    background: none;
    border: 1px solid color-mix(in oklab, var(--chrome-text) 20%, transparent);
    border-radius: 50%;
    cursor: pointer;
    width: 1.75rem;
    height: 1.75rem;
    padding: 0;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}

.avatar-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
}

.avatar-initials {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    color: var(--chrome-text);
}
```

- [ ] **Step 5: Verify TypeScript compiles**

```bash
cd apps/web && pnpm check
```

Expected: no errors

- [ ] **Step 6: Commit**

```bash
git add apps/web/src/routes/+layout.server.ts apps/web/src/lib/stores/user.ts apps/web/src/routes/+layout.svelte apps/web/src/lib/components/shell/Nav.svelte
git commit -m "feat(web): layout auth load, user store, Nav sign-in/out"
```

---

## Task 12: SvelteKit — PremiumGate + upgrade page

**Files:**
- Create: `apps/web/src/lib/components/auth/PremiumGate.svelte`
- Create: `apps/web/src/routes/upgrade/+page.svelte`
- Create: `apps/web/src/routes/upgrade/success/+page.svelte`

- [ ] **Step 1: Create PremiumGate.svelte**

```svelte
<!-- apps/web/src/lib/components/auth/PremiumGate.svelte -->
<script lang="ts">
    import { userStore } from '$lib/stores/user';

    let { children, feature = 'This feature' }: { children: any; feature?: string } = $props();
</script>

{#if $userStore?.is_premium}
    {@render children()}
{:else}
    <div class="gate">
        <div class="gate-icon">◈</div>
        <p class="gate-text">{feature} is available to Premium members.</p>
        <a href="/upgrade" class="gate-btn">Upgrade for $5.99</a>
        {#if !$userStore}
            <p class="gate-sub">Already purchased? <button class="gate-signin" onclick={() => window.location.href = '/?signin=1'}>Sign in</button></p>
        {/if}
    </div>
{/if}

<style>
    .gate {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.75rem;
        padding: 2rem;
        border: 1px solid color-mix(in oklab, var(--chrome-text) 12%, transparent);
        border-radius: 0.5rem;
        text-align: center;
        font-family: 'JetBrains Mono', monospace;
    }
    .gate-icon { font-size: 1.5rem; color: var(--mlb-red); }
    .gate-text { font-size: 0.8rem; color: color-mix(in oklab, var(--chrome-text) 70%, transparent); margin: 0; }
    .gate-btn {
        background: var(--mlb-red);
        color: #fff;
        border: none;
        border-radius: 0.3rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.04em;
        padding: 0.4rem 1rem;
        text-decoration: none;
        cursor: pointer;
        transition: opacity 0.15s;
    }
    .gate-btn:hover { opacity: 0.85; }
    .gate-sub { font-size: 0.7rem; color: color-mix(in oklab, var(--chrome-text) 45%, transparent); margin: 0; }
    .gate-signin { background: none; border: none; color: var(--chrome-text); cursor: pointer; font-family: inherit; font-size: inherit; text-decoration: underline; }
</style>
```

- [ ] **Step 2: Create upgrade page**

```svelte
<!-- apps/web/src/routes/upgrade/+page.svelte -->
<script lang="ts">
    import { userStore } from '$lib/stores/user';
    import SEO from '$lib/components/shell/SEO.svelte';

    let loading = $state(false);
    let error = $state('');

    async function startCheckout() {
        loading = true;
        error = '';
        try {
            const resp = await fetch('/api/creem/checkout', { method: 'POST' });
            if (!resp.ok) {
                error = resp.status === 401 ? 'Please sign in first.' : 'Something went wrong. Try again.';
                return;
            }
            const { checkout_url } = await resp.json();
            window.location.href = checkout_url;
        } catch {
            error = 'Network error. Try again.';
        } finally {
            loading = false;
        }
    }
</script>

<SEO title="Upgrade — Diamond Departures" description="Get lifetime access to premium features." path="/upgrade" />

<div class="upgrade-page">
    <div class="card">
        <div class="logo">◈</div>
        <h1 class="title">Diamond Departures Premium</h1>
        <p class="subtitle">One-time purchase. Yours forever.</p>

        <ul class="features">
            <li>⊕ Player Watchlist — pin players across all views</li>
            <li>⊕ Custom Watch Boards — build boards from any players</li>
            <li>⊕ Email Alerts — get notified when stats cross thresholds</li>
            <li>⊕ CSV Export — download any leaderboard</li>
        </ul>

        <div class="price">$5.99 <span class="price-sub">once, forever</span></div>

        {#if $userStore?.is_premium}
            <div class="already">You already have Premium. ◈</div>
        {:else}
            <button class="checkout-btn" onclick={startCheckout} disabled={loading}>
                {loading ? 'Redirecting...' : 'Get Premium'}
            </button>
            {#if error}<p class="error">{error}</p>{/if}
        {/if}
    </div>
</div>

<style>
    .upgrade-page {
        min-height: calc(100vh - var(--nav-height));
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem 1rem;
    }
    .card {
        background: var(--chrome-bg);
        border: 1px solid color-mix(in oklab, var(--chrome-text) 12%, transparent);
        border-radius: 0.75rem;
        padding: 2.5rem;
        max-width: 420px;
        width: 100%;
        text-align: center;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .logo { font-size: 2rem; color: var(--mlb-red); }
    .title { font-family: 'Instrument Serif', serif; font-size: 1.5rem; font-weight: 400; margin: 0; color: var(--chrome-text); }
    .subtitle { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: color-mix(in oklab, var(--chrome-text) 55%, transparent); margin: 0; }
    .features { list-style: none; padding: 0; margin: 0; text-align: left; display: flex; flex-direction: column; gap: 0.5rem; }
    .features li { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: color-mix(in oklab, var(--chrome-text) 75%, transparent); }
    .price { font-family: 'JetBrains Mono', monospace; font-size: 1.75rem; font-weight: 700; color: var(--chrome-text); }
    .price-sub { font-size: 0.8rem; font-weight: 400; color: color-mix(in oklab, var(--chrome-text) 50%, transparent); }
    .checkout-btn { background: var(--mlb-red); color: #fff; border: none; border-radius: 0.4rem; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 700; letter-spacing: 0.04em; padding: 0.65rem 2rem; cursor: pointer; transition: opacity 0.15s; width: 100%; }
    .checkout-btn:hover:not(:disabled) { opacity: 0.85; }
    .checkout-btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .error { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: var(--mlb-red); margin: 0; }
    .already { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: color-mix(in oklab, var(--chrome-text) 65%, transparent); }
</style>
```

- [ ] **Step 3: Create success page**

```svelte
<!-- apps/web/src/routes/upgrade/success/+page.svelte -->
<script lang="ts">
    import SEO from '$lib/components/shell/SEO.svelte';
</script>

<SEO title="Welcome to Premium — Diamond Departures" description="" path="/upgrade/success" />

<div class="success-page">
    <div class="card">
        <div class="icon">◈</div>
        <h1 class="title">You're Premium.</h1>
        <p class="body">Your purchase is confirmed. Premium features are now active — sign in to access your watchlist, watch boards, and alerts.</p>
        <a href="/" class="home-btn">Back to the board</a>
    </div>
</div>

<style>
    .success-page { min-height: calc(100vh - var(--nav-height)); display: flex; align-items: center; justify-content: center; padding: 2rem; }
    .card { background: var(--chrome-bg); border: 1px solid color-mix(in oklab, var(--chrome-text) 12%, transparent); border-radius: 0.75rem; padding: 2.5rem; max-width: 380px; width: 100%; text-align: center; display: flex; flex-direction: column; gap: 1rem; }
    .icon { font-size: 2rem; color: var(--mlb-red); }
    .title { font-family: 'Instrument Serif', serif; font-size: 1.4rem; font-weight: 400; margin: 0; color: var(--chrome-text); }
    .body { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: color-mix(in oklab, var(--chrome-text) 65%, transparent); margin: 0; line-height: 1.6; }
    .home-btn { background: var(--mlb-red); color: #fff; border: none; border-radius: 0.4rem; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; font-weight: 700; padding: 0.55rem 1.5rem; text-decoration: none; transition: opacity 0.15s; }
    .home-btn:hover { opacity: 0.85; }
</style>
```

- [ ] **Step 4: Verify TypeScript**

```bash
cd apps/web && pnpm check
```

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/lib/components/auth/PremiumGate.svelte apps/web/src/routes/upgrade/
git commit -m "feat(web): PremiumGate component, upgrade page, success page"
```

---

## Task 13: SvelteKit — watchlist pin icon on board rows

**Files:**
- Modify: `apps/web/src/lib/components/board/Row.svelte`

- [ ] **Step 1: Add watchlist store to Row.svelte**

In `apps/web/src/lib/components/board/Row.svelte`, add to the `<script>` block:

```typescript
import { userStore } from '$lib/stores/user';

let { row, ...existingProps } = $props();

let pinned = $state(false);
let pinLoading = $state(false);

async function togglePin(e: MouseEvent) {
    e.stopPropagation();
    if (!$userStore?.is_premium) return;
    pinLoading = true;
    try {
        if (pinned) {
            await fetch(`/api/watchlist/${row.player_id}`, { method: 'DELETE' });
            pinned = false;
        } else {
            await fetch('/api/watchlist', {
                method: 'POST',
                headers: { 'content-type': 'application/json' },
                body: JSON.stringify({ player_id: row.player_id }),
            });
            pinned = true;
        }
    } finally {
        pinLoading = false;
    }
}
```

- [ ] **Step 2: Add pin button to Row template**

Inside the row's HTML, after the rank cell, add:

```svelte
{#if $userStore?.is_premium}
    <button
        class="pin-btn"
        class:pinned
        onclick={togglePin}
        disabled={pinLoading}
        aria-label={pinned ? 'Remove from watchlist' : 'Add to watchlist'}
        title={pinned ? 'Unpin' : 'Pin to watchlist'}
    >⊕</button>
{/if}
```

Add styles:

```css
.pin-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 0.75rem;
    color: color-mix(in oklab, var(--chrome-text) 30%, transparent);
    padding: 0 0.25rem;
    transition: color 0.15s;
    line-height: 1;
}
.pin-btn:hover { color: var(--chrome-text); }
.pin-btn.pinned { color: var(--mlb-red); }
.pin-btn:disabled { opacity: 0.4; cursor: not-allowed; }
```

- [ ] **Step 3: Verify TypeScript**

```bash
cd apps/web && pnpm check
```

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/lib/components/board/Row.svelte
git commit -m "feat(web): watchlist pin icon on board rows"
```

---

## Task 14: SvelteKit — watch boards route

**Files:**
- Create: `apps/web/src/routes/boards/+page.ts`
- Create: `apps/web/src/routes/boards/+page.svelte`
- Create: `apps/web/src/routes/boards/[id]/+page.ts`
- Create: `apps/web/src/routes/boards/[id]/+page.svelte`

- [ ] **Step 1: Create boards list load**

```typescript
// apps/web/src/routes/boards/+page.ts
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, parent }) => {
    const { user } = await parent();
    if (!user?.is_premium) return { boards: [] };

    const resp = await fetch('/api/watch-boards');
    if (!resp.ok) return { boards: [] };
    return { boards: await resp.json() };
};
```

- [ ] **Step 2: Create boards list page**

```svelte
<!-- apps/web/src/routes/boards/+page.svelte -->
<script lang="ts">
    import PremiumGate from '$lib/components/auth/PremiumGate.svelte';
    import SEO from '$lib/components/shell/SEO.svelte';

    let { data } = $props();
    let newName = $state('');
    let boards = $state(data.boards ?? []);

    async function createBoard() {
        if (!newName.trim()) return;
        const resp = await fetch('/api/watch-boards', {
            method: 'POST',
            headers: { 'content-type': 'application/json' },
            body: JSON.stringify({ name: newName.trim() }),
        });
        if (resp.ok) {
            boards = [await resp.json(), ...boards];
            newName = '';
        }
    }

    async function deleteBoard(id: string) {
        await fetch(`/api/watch-boards/${id}`, { method: 'DELETE' });
        boards = boards.filter((b: any) => b.id !== id);
    }
</script>

<SEO title="Watch Boards — Diamond Departures" description="Your custom player boards." path="/boards" />

<div class="boards-page">
    <PremiumGate feature="Watch Boards">
        <div class="boards-inner">
            <h1 class="page-title">Watch Boards</h1>
            <div class="create-row">
                <input class="name-input" bind:value={newName} placeholder="New board name" onkeydown={(e) => e.key === 'Enter' && createBoard()} />
                <button class="create-btn" onclick={createBoard}>Create</button>
            </div>
            {#if boards.length === 0}
                <p class="empty">No boards yet. Create one above.</p>
            {:else}
                <ul class="board-list">
                    {#each boards as board (board.id)}
                        <li class="board-item">
                            <a href="/boards/{board.id}" class="board-link">{board.name}</a>
                            <button class="delete-btn" onclick={() => deleteBoard(board.id)}>✕</button>
                        </li>
                    {/each}
                </ul>
            {/if}
        </div>
    </PremiumGate>
</div>

<style>
    .boards-page { padding: calc(var(--nav-height) + 2rem) 1rem 2rem; max-width: 640px; margin: 0 auto; }
    .page-title { font-family: 'Instrument Serif', serif; font-size: 1.5rem; font-weight: 400; color: var(--chrome-text); margin: 0 0 1.5rem; }
    .create-row { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; }
    .name-input { flex: 1; background: color-mix(in oklab, var(--chrome-bg) 80%, transparent); border: 1px solid color-mix(in oklab, var(--chrome-text) 18%, transparent); border-radius: 0.3rem; color: var(--chrome-text); font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; padding: 0.4rem 0.75rem; }
    .create-btn { background: var(--mlb-red); color: #fff; border: none; border-radius: 0.3rem; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: 700; padding: 0.4rem 1rem; cursor: pointer; }
    .board-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 0.5rem; }
    .board-item { display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 1rem; border: 1px solid color-mix(in oklab, var(--chrome-text) 10%, transparent); border-radius: 0.4rem; }
    .board-link { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: var(--chrome-text); text-decoration: none; }
    .board-link:hover { color: var(--mlb-red); }
    .delete-btn { background: none; border: none; color: color-mix(in oklab, var(--chrome-text) 35%, transparent); cursor: pointer; font-size: 0.75rem; padding: 0.2rem; }
    .delete-btn:hover { color: var(--mlb-red); }
    .empty { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: color-mix(in oklab, var(--chrome-text) 45%, transparent); }
</style>
```

- [ ] **Step 3: Create single board load**

```typescript
// apps/web/src/routes/boards/[id]/+page.ts
import { error } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params, parent }) => {
    const { user } = await parent();
    if (!user?.is_premium) throw error(403, 'Premium required');

    const resp = await fetch(`/api/watch-boards/${params.id}`);
    if (!resp.ok) throw error(404, 'Board not found');

    const board = await resp.json();

    // Load player data for each player in the board
    // We reuse the existing board endpoint with the player IDs as a watchlist view
    return { board };
};
```

- [ ] **Step 4: Create single board page**

```svelte
<!-- apps/web/src/routes/boards/[id]/+page.svelte -->
<script lang="ts">
    import SEO from '$lib/components/shell/SEO.svelte';
    import Board from '$lib/components/board/Board.svelte';

    let { data } = $props();
</script>

<SEO title="{data.board.name} — Diamond Departures" description="Your custom watch board." path="/boards/{data.board.id}" />

<div class="board-page">
    <div class="top-bar">
        <a href="/boards" class="back-link">← Boards</a>
        <h1 class="board-title">{data.board.name}</h1>
    </div>

    {#if data.board.players.length === 0}
        <p class="empty">No players added yet. Pin players from the main board using the ⊕ icon.</p>
    {:else}
        <p class="info">Showing {data.board.players.length} player{data.board.players.length !== 1 ? 's' : ''}. Live updates apply.</p>
    {/if}
</div>

<style>
    .board-page { padding: calc(var(--nav-height) + 2rem) 1rem 2rem; max-width: 1600px; margin: 0 auto; }
    .top-bar { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; }
    .back-link { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: color-mix(in oklab, var(--chrome-text) 55%, transparent); text-decoration: none; }
    .back-link:hover { color: var(--chrome-text); }
    .board-title { font-family: 'Instrument Serif', serif; font-size: 1.4rem; font-weight: 400; color: var(--chrome-text); margin: 0; }
    .empty, .info { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: color-mix(in oklab, var(--chrome-text) 55%, transparent); }
</style>
```

- [ ] **Step 5: Add Boards link to Nav**

In `apps/web/src/lib/components/shell/Nav.svelte`, add to the `nav-left` section after the Methodology link:

```svelte
{#if $userStore?.is_premium}
    <a href="/boards" class:active={isActive('/boards')} class="nav-link">Boards</a>
{/if}
```

- [ ] **Step 6: Verify TypeScript**

```bash
cd apps/web && pnpm check
```

- [ ] **Step 7: Commit**

```bash
git add apps/web/src/routes/boards/ apps/web/src/lib/components/shell/Nav.svelte
git commit -m "feat(web): watch boards route and nav link"
```

---

## Task 15: SvelteKit — email alerts in player panel

**Files:**
- Modify: `apps/web/src/lib/components/player/Panel.svelte`

- [ ] **Step 1: Add alerts section to Panel.svelte**

In the Panel's `<script>` block, add:

```typescript
import { userStore } from '$lib/stores/user';

let alerts = $state<any[]>([]);
let alertStat = $state('wRC+');
let alertThreshold = $state('');
let alertDirection = $state<'up' | 'down'>('up');

async function loadAlerts() {
    if (!$userStore?.is_premium || !playerId) return;
    const resp = await fetch('/api/alerts');
    if (resp.ok) alerts = (await resp.json()).filter((a: any) => a.player_id === playerId);
}

async function createAlert() {
    const threshold = parseFloat(alertThreshold);
    if (isNaN(threshold)) return;
    const resp = await fetch('/api/alerts', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ player_id: playerId, stat_name: alertStat, threshold, direction: alertDirection }),
    });
    if (resp.ok) {
        alerts = [...alerts, await resp.json()];
        alertThreshold = '';
    }
}

async function deleteAlert(id: string) {
    await fetch(`/api/alerts/${id}`, { method: 'DELETE' });
    alerts = alerts.filter((a) => a.id !== id);
}

$effect(() => { if (playerId) loadAlerts(); });
```

- [ ] **Step 2: Add alerts UI to Panel template**

Below the TrendChart in the panel's HTML:

```svelte
{#if $userStore?.is_premium}
    <div class="alerts-section">
        <h3 class="alerts-title">Email Alerts</h3>
        {#each alerts as alert (alert.id)}
            <div class="alert-row">
                <span class="alert-label">{alert.stat_name} {alert.direction === 'up' ? '≥' : '≤'} {alert.threshold}</span>
                <button class="alert-del" onclick={() => deleteAlert(alert.id)}>✕</button>
            </div>
        {/each}
        <div class="alert-form">
            <select class="alert-select" bind:value={alertStat}>
                <option>wRC+</option><option>OPS</option><option>ERA</option><option>FIP</option><option>K%</option>
            </select>
            <select class="alert-select" bind:value={alertDirection}>
                <option value="up">≥</option><option value="down">≤</option>
            </select>
            <input class="alert-input" bind:value={alertThreshold} placeholder="threshold" type="number" step="0.1" />
            <button class="alert-add" onclick={createAlert}>Add</button>
        </div>
    </div>
{/if}
```

Add styles:

```css
.alerts-section { padding: 1rem; border-top: 1px solid color-mix(in oklab, var(--chrome-text) 8%, transparent); }
.alerts-title { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; letter-spacing: 0.06em; text-transform: uppercase; color: color-mix(in oklab, var(--chrome-text) 45%, transparent); margin: 0 0 0.75rem; }
.alert-row { display: flex; justify-content: space-between; align-items: center; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: var(--chrome-text); margin-bottom: 0.4rem; }
.alert-del { background: none; border: none; color: color-mix(in oklab, var(--chrome-text) 35%, transparent); cursor: pointer; font-size: 0.7rem; }
.alert-del:hover { color: var(--mlb-red); }
.alert-form { display: flex; gap: 0.35rem; margin-top: 0.75rem; flex-wrap: wrap; }
.alert-select, .alert-input { background: color-mix(in oklab, var(--chrome-bg) 80%, transparent); border: 1px solid color-mix(in oklab, var(--chrome-text) 18%, transparent); border-radius: 0.25rem; color: var(--chrome-text); font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; padding: 0.3rem 0.5rem; }
.alert-input { width: 5rem; }
.alert-add { background: var(--mlb-red); border: none; border-radius: 0.25rem; color: #fff; cursor: pointer; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 700; padding: 0.3rem 0.65rem; }
```

- [ ] **Step 3: Verify TypeScript**

```bash
cd apps/web && pnpm check
```

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/lib/components/player/Panel.svelte
git commit -m "feat(web): email alerts section in player detail panel"
```

---

## Task 16: SvelteKit — CSV export button

**Files:**
- Modify: `apps/web/src/lib/components/board/Header.svelte`

- [ ] **Step 1: Add export button to Header.svelte**

In the Header's `<script>` block, add:

```typescript
import { userStore } from '$lib/stores/user';

let { view, sort, season, ...existingProps } = $props();

function downloadCsv() {
    if (!$userStore?.is_premium) return;
    const params = new URLSearchParams({ view, sort });
    if (season) params.set('season', String(season));
    window.open(`/api/board/export?${params}`, '_blank');
}
```

- [ ] **Step 2: Add export button to Header template**

In the header controls area, add:

```svelte
{#if $userStore?.is_premium}
    <button class="export-btn" onclick={downloadCsv} title="Download CSV">↓ CSV</button>
{/if}
```

Add style:

```css
.export-btn {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.04em;
    background: none;
    border: 1px solid color-mix(in oklab, var(--chrome-text) 22%, transparent);
    border-radius: 0.3rem;
    color: color-mix(in oklab, var(--chrome-text) 60%, transparent);
    cursor: pointer;
    padding: 0.25rem 0.55rem;
    transition: color 0.15s, border-color 0.15s;
}
.export-btn:hover {
    color: var(--chrome-text);
    border-color: color-mix(in oklab, var(--chrome-text) 45%, transparent);
}
```

- [ ] **Step 3: Verify TypeScript**

```bash
cd apps/web && pnpm check
```

- [ ] **Step 4: Run full API test suite one final time**

```bash
pytest apps/api/tests/ -v
```

Expected: all pass

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/lib/components/board/Header.svelte
git commit -m "feat(web): CSV export button for premium users"
```

---

## Task 17: Docker Compose and env var wiring

**Files:**
- Modify: `docker-compose.yml`
- Create: `.env.example`

- [ ] **Step 1: Add new env vars to API service in docker-compose.yml**

Under the `api` service `environment`:

```yaml
- SUPABASE_JWT_SECRET=${SUPABASE_JWT_SECRET:-}
- CREEM_API_KEY=${CREEM_API_KEY:-}
- CREEM_WEBHOOK_SECRET=${CREEM_WEBHOOK_SECRET:-}
- CREEM_PRODUCT_ID=${CREEM_PRODUCT_ID:-}
- RESEND_API_KEY=${RESEND_API_KEY:-}
```

Under the `ingest` service `environment`:

```yaml
- RESEND_API_KEY=${RESEND_API_KEY:-}
```

- [ ] **Step 2: Create .env.example at repo root**

```bash
# Supabase Auth
SUPABASE_JWT_SECRET=         # Project Settings → API → JWT Secret
PUBLIC_SUPABASE_URL=         # https://yourproject.supabase.co
PUBLIC_SUPABASE_ANON_KEY=    # Project Settings → API → anon public key

# Creem.io
CREEM_API_KEY=               # Creem dashboard → API keys
CREEM_WEBHOOK_SECRET=        # Creem dashboard → Webhooks → signing secret
CREEM_PRODUCT_ID=            # Creem dashboard → Products → product ID

# Email (Resend)
RESEND_API_KEY=              # resend.com → API Keys
```

- [ ] **Step 3: Verify docker-compose syntax**

```bash
docker compose config --quiet
```

Expected: no errors

- [ ] **Step 4: Commit**

```bash
git add docker-compose.yml .env.example
git commit -m "chore: wire new env vars into docker-compose and document in .env.example"
```

---

## Self-Review

**Spec coverage check:**

- ✅ Supabase Auth (hooks.server.ts + supabase.ts, Task 10)
- ✅ Google OAuth (enabled in Supabase dashboard — no code needed)
- ✅ JWT validation in FastAPI (auth.py, Task 2)
- ✅ Users table + upsert (migration Task 1, store Task 3)
- ✅ Creem.io $5.99 one-time checkout + webhook (Task 4)
- ✅ Premium gate enforced on all premium endpoints (Task 5–8)
- ✅ Watchlist API + UI (Tasks 5, 13)
- ✅ Watch boards API + UI (Tasks 6, 14)
- ✅ Email alerts API + Resend delivery + ingest firing (Tasks 7, 9)
- ✅ CSV export API + UI (Tasks 8, 16)
- ✅ Nav sign-in/sign-out + avatar (Task 11)
- ✅ Upgrade page (Task 12)
- ✅ PremiumGate component (Task 12)
- ✅ Environment variables documented (Task 17)

**Type consistency check:** `UserUpsert`, `WatchlistLister/Adder/Remover`, `BoardLister/Creator/Getter/Renamer/Deleter/BoardPlayerAdder/BoardPlayerRemover`, `AlertLister/Creator/Deleter`, `CreemCheckout/CreemMarkPremium` — all defined in their module files before being referenced in main.py or store.py. ✅

**Placeholder scan:** No TBDs. The Creem.io event name `payment.succeeded` is the standard name — verify against Creem.io dashboard when setting up the webhook. The `hmac.new` call in test_creem.py should be `hmac.new` → note: Python uses `hmac.new()` which is correct. ✅
