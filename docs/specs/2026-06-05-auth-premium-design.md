# Auth + Premium Features Design

**Date:** 2026-06-05
**Scope:** Supabase Auth, Creem.io one-time purchase, watchlist, watch boards, email alerts, CSV export

---

## Overview

The live leaderboard board remains free and public. Authentication and a $5.99 lifetime purchase unlock four premium features: player watchlist, custom watch boards, email alerts, and CSV export.

Auth is delegated entirely to Supabase Auth (hosted). FastAPI validates Supabase-issued JWTs and owns all premium business logic. SvelteKit stays a pure UI layer — it manages the Supabase session via `@supabase/ssr` and forwards the JWT to FastAPI for protected calls.

---

## Deployment Context

Both services deployed to Cloud Run with `ingress=internal-and-cloud-load-balancing`. Neither service is publicly accessible directly — all traffic routes through a GCP External Load Balancer:

```
Browser
  └── diamonddepartures.com (GCP External Load Balancer)
        ├── /api/* → FastAPI Cloud Run service
        └── /*     → SvelteKit Cloud Run service
```

Same-domain setup means `@supabase/ssr` cookies and FastAPI cookies share the root domain with no CORS complexity.

---

## Architecture

```
Browser
  ├── Supabase Auth (hosted) — OAuth dance, JWT issuance, token refresh
  └── diamonddepartures.com
        ├── SvelteKit — @supabase/ssr manages HttpOnly session cookies
        │     └── layout.server.ts calls /api/auth/me on every page load
        └── FastAPI — validates Supabase JWTs, owns all premium endpoints
              └── JWT middleware: verifies against SUPABASE_JWT_SECRET
```

### Auth flow

1. User clicks "Sign in" → Supabase JS client triggers OAuth (Google, or any enabled provider)
2. Supabase handles OAuth dance, issues access token (JWT) + refresh token
3. `@supabase/ssr` stores tokens in HttpOnly cookies
4. SvelteKit `+layout.server.ts` reads session from cookies, calls `GET /api/auth/me`
5. FastAPI validates the Supabase JWT, upserts the user in `public.users`, returns user + `is_premium`
6. User context flows down to all pages via `+layout.svelte`

For premium FastAPI calls: SvelteKit server-side load functions forward the Supabase access token as `Authorization: Bearer <token>`.

### JWT validation in FastAPI

FastAPI middleware verifies the Supabase JWT signature using `SUPABASE_JWT_SECRET` (available in the Supabase project dashboard). No external network call needed — pure local verification with `python-jose`.

---

## Database Schema

New migration: `apps/api/migrations/008_auth_and_premium.up.sql`

```sql
-- User record. id mirrors Supabase auth.users.id.
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

-- Named boards of hand-picked players.
CREATE TABLE watch_boards (
    id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name       text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE watch_board_players (
    board_id  uuid NOT NULL REFERENCES watch_boards(id) ON DELETE CASCADE,
    player_id int  NOT NULL REFERENCES players(id)     ON DELETE CASCADE,
    added_at  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (board_id, player_id)
);

-- Simple per-user pinned players (no named board).
CREATE TABLE watchlist_players (
    user_id   uuid NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
    player_id int  NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    added_at  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, player_id)
);

-- Stat threshold alerts.
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

Down migration drops all five tables in reverse dependency order.

---

## API Endpoints

### Auth

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/auth/me` | JWT (optional) | Upsert user, return user + is_premium. Re-called on every page load to propagate premium status. Returns 401 if no valid JWT. |
| POST | `/api/auth/logout` | — | No-op on FastAPI side; client clears Supabase session. Included for completeness. |

### Creem.io

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/creem/checkout` | JWT + authenticated | Creates Creem.io checkout session, returns `{ checkout_url }`. Passes `user_id` + `email` as metadata. |
| POST | `/api/creem/webhook` | None (signature check) | Receives Creem.io webhook. Verifies `CREEM_WEBHOOK_SECRET` signature. On `payment.succeeded`: sets `is_premium=true`, `purchased_at=now()`. |

### Watchlist (premium)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/watchlist` | Returns `[{ player_id, added_at }]` |
| POST | `/api/watchlist` | Body: `{ player_id }`. Adds player. |
| DELETE | `/api/watchlist/{player_id}` | Removes player. |

### Watch Boards (premium)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/watch-boards` | Lists all boards for user |
| POST | `/api/watch-boards` | Body: `{ name }`. Creates board. |
| GET | `/api/watch-boards/{id}` | Board metadata + player list |
| PUT | `/api/watch-boards/{id}` | Body: `{ name }`. Renames board. |
| DELETE | `/api/watch-boards/{id}` | Deletes board + players |
| POST | `/api/watch-boards/{id}/players/{player_id}` | Adds player to board |
| DELETE | `/api/watch-boards/{id}/players/{player_id}` | Removes player from board |

### Email Alerts (premium)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/alerts` | Lists user's alerts |
| POST | `/api/alerts` | Body: `{ player_id, stat_name, threshold, direction }` |
| DELETE | `/api/alerts/{id}` | Deletes alert |

### CSV Export (premium)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/board/export` | Same params as `/api/board`. Returns `text/csv` with `Content-Disposition: attachment; filename=diamond-departures.csv`. |

### Error responses

- `401 Unauthorized` — missing or invalid JWT
- `403 Forbidden` — valid JWT but `is_premium=false`
- `404 Not Found` — resource not found or belongs to another user

---

## Creem.io Webhook

Creem.io sends a POST with a signature header. FastAPI verifies using `CREEM_WEBHOOK_SECRET` before processing. The relevant event is `payment.succeeded` (or Creem.io's equivalent — confirm exact event name from their docs before implementation).

Premium status propagates to the user on their next page load via `/api/auth/me` — no polling or websocket needed.

---

## Email Alert Delivery

The ingest worker (`apps/ingest`) already runs on a schedule. After each leaderboard recomputation, it queries `email_alerts` for any thresholds crossed since `last_fired_at`, sends transactional emails via **Resend** (simple HTTP API, generous free tier), and updates `last_fired_at`.

Email provider: Resend (`resend.com`). One new env var: `RESEND_API_KEY`.

---

## Frontend Changes

### New dependencies

- `@supabase/supabase-js`
- `@supabase/ssr`

### New env vars (web)

- `PUBLIC_SUPABASE_URL`
- `PUBLIC_SUPABASE_ANON_KEY`

### New/modified files

| File | Change |
|------|--------|
| `src/lib/supabase.ts` | Supabase client factory (browser + server variants) |
| `src/hooks.server.ts` | `@supabase/ssr` session middleware — reads cookies, populates `event.locals.supabase` and `event.locals.user` |
| `src/app.d.ts` | Extend `Locals` with `supabase`, `user`, `session` |
| `src/routes/+layout.server.ts` | Calls `/api/auth/me`, passes user + is_premium to layout |
| `src/routes/+layout.svelte` | Receives user prop, initializes `userStore` |
| `src/lib/stores/user.ts` | Svelte store: `{ id, email, name, avatar_url, is_premium }` or `null` |
| `src/lib/components/shell/Nav.svelte` | "Sign in" button or avatar + dropdown |
| `src/lib/components/auth/PremiumGate.svelte` | Wraps premium UI; shows upgrade CTA if not premium |
| `src/routes/upgrade/+page.svelte` | Pricing page; calls `/api/creem/checkout`, redirects to Creem.io |
| `src/routes/boards/+page.svelte` | List + create watch boards |
| `src/routes/boards/[id]/+page.svelte` | Single watch board rendered with existing `Board.svelte` |
| `src/lib/components/board/Row.svelte` | Add watchlist pin icon (visible when signed in + premium) |
| `src/lib/components/player/Panel.svelte` | Add email alert section below trend chart |
| `src/lib/components/board/Header.svelte` | Add CSV export button (gated) |

---

## New Environment Variables

| Service | Variable | Description |
|---------|----------|-------------|
| FastAPI | `SUPABASE_JWT_SECRET` | From Supabase project settings → API → JWT Secret |
| FastAPI | `CREEM_API_KEY` | Creem.io API key for creating checkout sessions |
| FastAPI | `CREEM_WEBHOOK_SECRET` | Creem.io webhook signing secret |
| FastAPI | `CREEM_PRODUCT_ID` | Creem.io product ID for the $5.99 lifetime purchase |
| FastAPI | `RESEND_API_KEY` | For transactional email alerts |
| SvelteKit | `PUBLIC_SUPABASE_URL` | Supabase project URL |
| SvelteKit | `PUBLIC_SUPABASE_ANON_KEY` | Supabase anon/public key |

---

## What Stays the Same

- The live board is fully public — no auth check on `/api/board` or `/api/board/sse`
- Existing migrations (001–007) untouched
- Ingest worker logic untouched except for the alert-firing addition at the end of each leaderboard recomputation cycle
- Split-flap animation engine, SSE, all board views — unchanged

---

## Out of Scope

- Email verification (Supabase handles this)
- Password auth (Supabase handles this if ever enabled)
- Subscription management UI (Creem.io hosts this)
- Refunds (handled via Creem.io dashboard)
- Watch board SSE live updates (watch boards render as a static snapshot of the existing board data; live updates are a future enhancement)
