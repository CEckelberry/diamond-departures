# Diamond Departures

> Top 100 active MLB players ranked by sabermetrics, styled as a Penn Station split-flap board, updating live during games.

The aesthetic of an old train station departure board — letters and digits physically rotating when they change — applied to a leaderboard of the best baseball players right now. As stats update mid-game, rows reshuffle and individual cells flip to their new values. As Judge gets a hit and his wRC+ ticks up, the cell flips. As Soto's xFIP climbs after a rough inning, his row drops three spots and the rank cell flips on every row that moved.

It's a baseball nerd's dream rendered as a working dashboard.

## What this is

A single-page app with three primary views, all live:

- **All hitters** ranked by wRC+ (the gold-standard rate stat for offense)
- **All pitchers** ranked by FIP (the gold-standard for run prevention)
- **By position** — top players at C, 1B, 2B, 3B, SS, LF, CF, RF, DH, SP, RP

Each view shows the top 100 in real time. Clicking any player opens a detailed card with their full stat line, recent game logs, and a small visualization of their season trend.

A "stat picker" in each view lets you re-rank by any of ~20 sabermetric stats: AVG, OBP, SLG, OPS, wRC+, wOBA, BABIP, ISO, DRS, UZR/150, OAA for hitters; ERA, FIP, xFIP, SIERA, ERA+, K/9, BB/9, K-BB%, WHIP for pitchers. The leaderboard re-sorts and animates every cell that moved.

## What this isn't

- Not a fantasy baseball site. There are no projections, no recommendations, no draft tools.
- Not a real-time scoring service. We don't show pitch-by-pitch; we show the leaderboard *responding* to game events.
- Not a historical encyclopedia. We track current-season stats with rolling history. For deep history, Baseball Reference exists.
- Not a betting tool. There are no odds, no money lines, no anything financial.
- Not affiliated with MLB. We use public stat data, branded carefully (no logos we don't have rights to).

## Repository layout

```
diamond/
├── README.md
├── DATA.md                  ← stat sources, freshness, off-season, position taxonomy
├── ARCHITECTURE.md          ← system design, ingestion, SSE, caching
├── DESIGN.md                ← visual language, the split-flap mechanic
├── STATS.md                 ← every stat we display: formula, range, how to read
├── TASKS.md                 ← phased build plan
├── apps/
│   ├── web/                 ← SvelteKit frontend (the split-flap board)
│   ├── api/                 ← FastAPI service: SSE broadcast, leaderboard queries
│   └── ingest/              ← Python worker/job: pulls MLB Stats API, computes derived stats
├── packages/
│   ├── stats/               ← shared sabermetric formulas (used by ingest + api)
│   └── content/             ← player metadata, position taxonomy, descriptions
├── infra/
│   ├── terraform/           ← Cloud Run, Cloud SQL, Cloud Scheduler, DNS
│   └── docker/
├── scripts/                 ← local dev + agent orchestration helpers
├── orchestration/           ← task packets, check-ins, run artifacts
└── .github/workflows/
```

## Stack at a glance

- **Frontend**: SvelteKit, TypeScript, Tailwind v4, custom split-flap component (no library — it has to feel right)
- **API**: Python `FastAPI`, Server-Sent Events for live updates, `asyncpg`/`SQLAlchemy` for Postgres
- **Ingest**: Python Cloud Run job (non-HTTP worker) triggered by Cloud Scheduler. Runs every 60 seconds during games, every hour off-game, daily off-season.
- **Database**: Cloud SQL Postgres 18, `db-custom-1-3840` (1 vCPU, 3.75GB)
- **Stat source (v1)**: MLB Stats API (free, official, sufficient). FanGraphs scraping considered and rejected — see DATA.md.
- **Hosting**: Cloud Run for frontend, api, ingest. Cloud SQL for the database. Cloud Scheduler for ingest cadence.
- **Cost target**: ~$25-35/month, hard-capped at $50/month.

## Three modes of viewing

**The board** (default). The full top-100 leaderboard with split-flap mechanics. Click any row for a player detail card. The default sort is wRC+ for hitters, switchable in one click.

**By position**. Same board, filtered to a single position (e.g., "top SS by wRC+"). Smaller list (typically 20-30 qualifying players), so the board feels less dense and more focused.

**Player detail**. A modal or side panel showing one player: full stat line across multiple categories, recent game-by-game performance, season trend chart for the currently-active stat. Closes back to wherever the visitor came from.

## Why this is a good portfolio project

It demonstrates:

- **Real-time backend work** — SSE channels per-view, change detection, broadcast efficiency
- **Animation that matters** — the split-flap is *the* feature; getting it to feel snappy without being chaotic is real frontend craft
- **Data pipeline thinking** — stat ingestion, schema-stable computation, off-season handling, drift detection
- **Domain knowledge done right** — sabermetrics has its own vocabulary; doing it well shows depth
- **Honest framing of data sources** — MLB Stats API has gaps; the case study explains them

It also has the highest "share-on-Twitter" ceiling of the four projects. Beautiful animation + recognizable players + a niche audience = the kind of thing baseball Twitter loves.

## Read order

If you're starting from zero:

1. `DATA.md` first — every architectural decision flows from how we get stats and how fresh they are
2. `STATS.md` second — what we're actually computing
3. `ARCHITECTURE.md` third — how it's wired
4. `DESIGN.md` fourth — how it looks and moves
5. `TASKS.md` last — the build plan

Pin DATA.md and ARCHITECTURE.md in any Claude Code session that touches the backend or pipeline. Pin DESIGN.md for any frontend work. STATS.md is reference material — handy when implementing a specific computation, less needed otherwise.

## When to build this

Recommended slot in the portfolio buildout: **third project to ship**, after Backend Bake-off and Terraplane.

Reasoning: Diamond depends on a live data source (MLB Stats API) which is most useful to demonstrate during baseball season (April through October). If you're shipping in November-March, the off-season presentation is the *only* thing visitors see, which undersells the project. Better to time the launch with at least a few weeks of regular-season games left so the live aspect is the first impression.

If timing pushes the build into off-season, ship a "preview mode" that replays a recent week of games at accelerated speed so visitors can see the split-flap mechanic in action even without live games.
