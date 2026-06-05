# Diamond Departures

> MLB's best players, ranked live by sabermetrics, rendered as a Penn Station split-flap departure board.

As Judge gets a hit and his wRC+ ticks up, the cell physically flips to its new value. As a pitcher's ERA climbs in the third inning, his row drops four spots and every rank cell that moved animates in sequence. The board sounds like a real departure board — mechanical clicks on every flip, a scoreboard chime when the rankings shift.

---

## What it does

A live leaderboard of MLB's top players with a split-flap animation engine built from scratch. No animation library. Every flip is a custom CSS 3D transform with tuned easing curves: free fall, mechanical stop, overshoot, damped bounce.

**Board views**
- Hitters ranked by any of 15+ stats (wRC+, wOBA, OPS, ISO, BABIP, BB%, K%, AVG, HR, RBI, SB, OBP, SLG, xBA, barrel %, hard hit %, exit velocity)
- Pitchers ranked by ERA, FIP, xFIP, K%, WHIP, K/9, BB/9, K-BB%, W, SV
- Defense view ranked by DRS, OAA, UZR, Def, Fielding %
- Positions view filtered by fielding position
- Sabermetric, Traditional, and Statcast stat tabs

**Live updates**
- SSE stream pushes rank changes and stat deltas mid-game
- Rows animate to new positions via Svelte's `flip` directive
- Individual stat cells flip through intermediate glyphs on change
- `▲N` / `▼N` rank change badges fade in and out on moving rows

**Big screen mode**
- Press `F` or click `⛶` to enter native fullscreen
- All controls hide, leaving only the board and the "◈ Diamond Departures" serif logo
- Press `Esc` or `F` to exit

**Sound**
- Synthesized via `OfflineAudioContext` → WAV blob → Audio element (no audio files)
- Mechanical white-noise click on each cell flip
- Cascading burst when many cells flip together
- Ascending or descending pentatonic chime when rankings shift, scaled by magnitude (2–4 notes for 1–2, 3–5, 6+ spot moves)

**Season selector**
- Any season 2016–present
- LIVE indicator when viewing the current season during games
- Off-season banner with next season info

**Player detail**
- Click any row for a stat panel with full season totals and recent game history

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | SvelteKit 2, TypeScript, Tailwind v4 |
| Animation | Custom split-flap engine (CSS 3D, no library) |
| API | FastAPI, Server-Sent Events, asyncpg |
| Ingest | Python worker — MLB Stats API → Postgres |
| Database | PostgreSQL 18 |
| Dev | Docker Compose (web + api + db + mlb-mock) |

---

## Running locally

```bash
docker compose up
```

The board runs at `http://localhost:5174`. The API is at `http://localhost:18000`.

To seed or backfill historical stats:

```bash
# inside the ingest container or virtualenv
python -m apps.ingest backfill --season 2026
```

---

## Repo layout

```
diamond-departures/
├── apps/
│   ├── web/          # SvelteKit frontend
│   │   ├── src/lib/
│   │   │   ├── audio/        # OfflineAudioContext synthesis
│   │   │   ├── components/
│   │   │   │   ├── board/    # Board, Row, Header, ViewTabs, StatPicker, SeasonPicker
│   │   │   │   ├── flap/     # Cell, Word — the split-flap engine
│   │   │   │   ├── player/   # Detail panel
│   │   │   │   └── shell/    # Nav, Footer, SEO
│   │   │   └── stores/       # board, sound, bigScreen, eink
│   │   └── static/
│   ├── api/          # FastAPI — /board, /board/sse, /players, /season-state
│   │   └── migrations/
│   └── ingest/       # MLB Stats API → leaderboard_views
├── packages/
│   └── stats/        # Sabermetric formulas shared between ingest + api
├── docker-compose.yml
└── Makefile
```

---

## Architecture

**Ingest** runs on a schedule, pulls from the MLB Stats API, computes derived stats (wRC+, BABIP, FIP, etc.), and writes ranked rows to `leaderboard_views` in Postgres — one row per `(view_key, sort_stat, season, player)`.

**API** has two board endpoints:
- `GET /api/board` — snapshot of current leaderboard (server-side rendered initial load)
- `GET /api/board/sse` — SSE stream that polls for DB changes and pushes rank/stat deltas

**Frontend** opens the SSE stream after page load and applies deltas with `applyDelta`, which triggers the animation engine. The split-flap engine queues intermediate glyphs and schedules each flip with `setTimeout`, staggered by row and column index to stay within GPU compositor budget (~560 simultaneous animated cells).

---

## What's next

Authentication (Google OAuth), Stripe subscriptions, and premium features:
- Custom watch boards — build a named board with hand-picked players or whole teams
- Player watchlist — pin players highlighted across all views
- Email alerts on stat moves
- Export to CSV
