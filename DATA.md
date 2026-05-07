# Data

This document defines where stats come from, how fresh they are, and how we handle the edge cases (off-season, position ambiguity, partial-season data). It is the most important document in the repository — every other decision (API design, cache strategy, UI states) flows from these rules.

A real baseball nerd reading this site will check, within 30 seconds, whether our numbers match Baseball Reference or FanGraphs. If they do, the site is credible. If they don't (or if the source is unclear), nothing else matters.

---

## Core principle

> Every stat shown on the site has a source, a freshness, and a method. The site exposes all three on demand. We never present a stale number as fresh, never present a derived number without showing how it was derived, and never paper over the off-season with fake activity.

The DATA rules below exist to make those promises keepable.

---

## Stat sources

Three potential sources, each evaluated:

### MLB Stats API (chosen)

The official MLB API at `statsapi.mlb.com`. Free, no API key required, generous rate limits (we'll never hit them at our scale).

**Pros:**
- Authoritative — these are the numbers MLB itself uses
- Updates within seconds of each pitch during live games
- Stable schema (mostly — see drift detection below)
- Covers all 30 teams, full active roster, full minor league system if we ever need it
- Returns historical data back to the early 1900s

**Cons:**
- Doesn't pre-compute advanced sabermetrics. We get raw counts (hits, ABs, K, BB) and basic rates (AVG, OBP, SLG, ERA, WHIP). Anything beyond requires us to compute it ourselves. **wRC+, FIP, xFIP, SIERA, DRS, UZR — all computed by us from raw data.**
- Defensive metrics (DRS, UZR, OAA) are partially available but require Statcast data, which is a separate API surface
- Park factors and league-adjustments require additional context tables we maintain ourselves

### FanGraphs (rejected)

The de facto home of sabermetrics. Has every stat we want, pre-computed.

**Pros:** comprehensive, authoritative for advanced stats, the source most fans trust.

**Rejected because:**
- No public API. Scraping would be against ToS.
- A paid data feed exists but is enterprise-priced. Out of scope for a portfolio project.
- Even if we negotiated access, the legal/credit obligations would complicate the project.

### Baseball Savant / Statcast (partially used)

MLB's tracking-tech site. Provides batted-ball data, exit velocities, sprint speeds, and the metrics derived from them (xBA, xSLG, OAA, Sprint Speed).

**Pros:** the most modern stat layer. xwOBA and OAA are newer-generation metrics that traditional stats can't replicate.

**Used for:** Statcast-derived stats only (xBA, xSLG, xwOBA, OAA, Sprint Speed). Same parent organization as MLB Stats API, accessed via a sibling endpoint. Minor extra integration work.

**Compromise we accept:** at v1, only the most popular Statcast stats are surfaced. Adding the full Statcast catalog is a v2 stretch.

---

## What we compute ourselves

Anything beyond raw counting stats requires our own computation. We maintain a `packages/stats/` library with implementations of:

| Stat | Formula source | Verification |
|---|---|---|
| **wRC+** | FanGraphs glossary, league-context | Spot-check against FanGraphs.com weekly |
| **wOBA** | wOBA weights table (Tom Tango) | Same |
| **FIP** | `((13*HR + 3*(BB+HBP) - 2*K) / IP) + cFIP` | Same |
| **xFIP** | FIP with league-average HR/FB rate | Same |
| **SIERA** | The Hardball Times formula | Same |
| **ERA+** | `100 * (lgERA / ERA) * PF` | Spot-check vs Baseball Reference |
| **OPS+** | `100 * (OBP/lgOBP + SLG/lgSLG - 1) * PF` | Same |
| **ISO** | `SLG - AVG` | Trivial |
| **BABIP** | `(H - HR) / (AB - K - HR + SF)` | Trivial |
| **K/9, BB/9, K-BB%** | Direct rate computation | Trivial |

The `packages/stats/` library is the single source of truth for these formulas. The api service queries it; the ingest service queries it; both must produce the same number for the same inputs. A test suite verifies this against ~50 hand-curated player-seasons where the correct values are documented.

**The verification problem.** Sabermetric formulas have multiple variants. The wRC+ implementation FanGraphs uses differs slightly from Baseball Reference's. We document which variant we use and why. Generally we follow FanGraphs because that's what most fans recognize. The case study links to our formula doc.

---

## Freshness contract

Every stat displayed on the site has a freshness signature, computed at query time:

- **Live (< 60s)** — game in progress, this stat updated within the last minute
- **Recent (< 1h)** — game finished recently, or a regular ingest just ran
- **Stale (< 24h)** — last ingest was within a day, but no new games or updates
- **Old (>= 24h)** — something is wrong; alert fires

The UI shows freshness via a small dot next to each stat:
- Solid teal: live
- Hollow teal: recent
- Hollow gray: stale
- Solid pink: old (something is wrong)

Hovering the dot shows the exact age ("updated 23s ago") and the source ("MLB Stats API · gameday feed").

### How we keep stats fresh

The ingest service runs at three different cadences:

| State | Cadence | What runs |
|---|---|---|
| Live games (≥1 game in progress) | every 60s | Live game feed → stat deltas → DB write → SSE broadcast |
| Between games (no live, recent activity) | every 15min | Box score reconciliation, daily roll-up |
| Off-game day (during season) | every 1h | Roster check, injury updates, transaction log |
| Off-season | once per day at 4am UTC | Roster freeze check, daily news ingestion (light) |

Cloud Scheduler triggers each. The ingest service exits after each run; it's not always-on.

### When a stat ages

If a stat shows up as "stale" (>1h since last update) during the regular season, the next ingest run should refresh it. If it's still stale on the run after, something's wrong (provider down, schema change, our query broken). Alert fires.

If a stat shows up as "old" (>24h) at all, we've missed multiple ingest runs. The site shows a banner: "Data updates have been delayed. We're investigating." This is the only honest response.

---

## The off-season problem

Baseball is dormant from early November to late March. During that window, the site has nothing live to show. The natural temptation is to make something up — fake activity, animated standings from last year, a "coming soon" banner. All of those are bad answers for a credibility-first project.

**What we do instead:**

The site has three season modes, displayed prominently and honestly:

### Mode 1 — In-season, games today

Default operation. Live updates, full split-flap mechanic, current standings.

### Mode 2 — In-season, no games today

Last night's box scores have been ingested. The board shows current standings as of last game. The freshness dots show "recent" not "live." A small banner: "No games until [next game] · [N hours]". The split-flap mechanic still works for stat-picker changes (when the visitor re-sorts), but doesn't auto-flip from data updates.

### Mode 3 — Off-season

The board shows final season stats. A different banner replaces the live indicator: "**[Year] regular season · final**". Players are still ranked, the split-flap still works for re-sorts, but the banner is permanent and the freshness dots are all gray.

A "preview mode" toggle in mode 3 replays a recent week of in-season activity at accelerated speed (5 minutes of real time = a full week of games). This lets visitors who arrive in February still see the split-flap responding to data changes. The preview is clearly labeled — no pretense that it's live. The case study mentions this as a deliberate decision.

### The transition between modes

Mode changes happen automatically based on the MLB schedule. The api service queries `statsapi.mlb.com/api/v1/seasons/current` on every request (cached 5 minutes) and selects the appropriate mode. No manual flag, no risk of forgetting to flip a switch.

---

## Position taxonomy

A starting pitcher and a reliever both pitch, but their stats are incomparable (a starter's ERA over 180 innings means something different from a reliever's over 60). A second baseman who plays 30 games at SS isn't really a SS. The taxonomy of "what counts as which position" is genuinely messy.

We resolve it with these rules:

### For position players (non-pitchers)

A player's **primary position** is the position where they have the most games played in the current season. Ties broken by innings played.

- A player with 80 games at 2B and 25 at SS is a 2B
- A player with 45 games at LF and 45 games at RF is "OF" (outfielder, no specific corner)
- A player with games across 3+ positions is a "UT" (utility)

Position eligibility (e.g., for the position-filtered views) is more lenient: any position the player has played 5+ games at this season. So a 2B who's played 25 games at SS shows up in *both* the 2B and SS views.

### For pitchers

We split into **starter (SP)** and **reliever (RP)** based on usage pattern:

- Starter: more than 50% of appearances were starts
- Reliever: less than 50%
- Each ranks against its own pool. A reliever with a 2.10 ERA does not appear on the SP leaderboard.

The "long reliever" / "spot starter" boundary is fuzzy. We follow the MLB.com classification when ambiguous.

### Designated hitter

DH is a position. A player with 70 DH games and 25 at 1B is a DH. The DH leaderboard is its own view.

### Multi-position eligibility view

A v2 stretch idea: a "fantasy-eligible" view that shows players ranked at every position they qualify at, useful for fantasy players. Skipped at v1.

---

## Player roster management

The active player pool is ~750 players (40-man rosters across 30 teams). Of those, ~100-150 are top-100-leaderboard contenders. We track all 750 to enable position filtering and the full stat catalog.

### Source of truth for "who's active"

The MLB roster API returns the 40-man roster of every team. We snapshot this daily and compute deltas. New call-ups appear in the leaderboard the day after they're rostered; demotions persist for 7 days then drop off (so a quick call-down doesn't make a player vanish mid-day).

### Minimum playing-time thresholds

To prevent a player with 1 AB and a 1.000 AVG from topping the leaderboard, we apply qualifying minimums:

- **Hitters**: 2.7 plate appearances per team game played. For half-season, that's roughly 220 PA.
- **Starters**: 1.0 IP per team game played. ~80 IP at midseason.
- **Relievers**: 25 appearances. (Standard MLB qualifier.)

Below the threshold, players don't appear on the main leaderboard. They show up in position-filtered views with a small "(unqualified)" tag and are visually de-emphasized.

The "qualified" status itself is a real-time stat — a hitter who hits the threshold mid-game suddenly appears on the leaderboard, with a small ("just qualified") badge for 24 hours. This is one of the most fun moments the split-flap UI can render: a row sliding in from below the visible list because someone just qualified.

---

## Schema drift

The MLB Stats API doesn't have a formal versioning contract. Schemas change without notice. We've seen:

- Field renames in seasonal updates
- New nested objects added (which is fine)
- Field removals (which is not fine)
- Calculation changes (e.g., a stat computed differently after a rule change)

### Drift detection

The ingest service maintains a "shape signature" for every endpoint we query: a hash of the JSON structure (keys at every level, ignoring values). On every ingest run, we compute the current signature and compare to the last known. Mismatch → log, compute new signature, continue running. If the mismatch causes a parse failure, we alert.

A weekly job dumps recent signatures and emails them. Even silent schema changes (key renames that we still happen to handle) become visible.

### Recovery from a bad ingest

If an ingest run produces clearly-wrong data (e.g., wRC+ values 10x normal), we have a "rollback to last good" mechanism: the stats table is append-only with a `valid_from` and `valid_to` timestamp. A bad ingest can be marked `valid_to = ingested_at` for all its writes, restoring the previous values. This is manual at v1 — no automated rollback. The case study calls this out.

---

## Verification: how we prove the numbers

The case study and the live site both need to demonstrate that the numbers we show are real. Three concrete checks:

### 1. Spot-check pipeline

A weekly Cloud Function compares 20 randomly-selected stat values from our DB to the corresponding values from MLB Stats API and FanGraphs (where the latter is publicly visible). Logs any mismatches > 0.5% relative deviation. Reviewed manually each week.

### 2. Public formula doc

`STATS.md` documents every formula we use. The case study links to it. Anyone who disagrees with our wRC+ value for a given player can look at the doc, verify the formula, and run the math themselves with raw stats from MLB.com.

### 3. Per-stat source attribution

The site exposes (on hover or click) the source of every displayed stat. "wRC+ · computed · sources: AVG, OBP, SLG, league-context · last update: 23s ago." Engineers and stat nerds will look for this.

---

## Things this data design cannot do

In the spirit of being honest about limits:

- **Pre-2008 advanced stats.** Statcast started in 2015. Pre-Statcast we don't have OAA, exit velocity, or sprint speed.
- **Defensive metrics for catchers.** Framing runs require pitch-tracking data not exposed via free APIs. We omit defensive ranking for catchers entirely (with a note explaining why).
- **Minor league players.** The MLB API exposes them but stats are inconsistent. Out of scope for v1.
- **International leagues.** NPB, KBO, Cuban national league players don't appear unless they sign with an MLB team.
- **Real-time injury status.** We track roster changes daily, not in real time. A player who left a game with an injury at 7pm won't be reflected until the next ingest run picks up the transaction (typically the next morning).

These limits go in the case study. They build trust by surfacing limits before someone else does.

---

## What "live" actually means

The split-flap aesthetic implies real-time. The technical reality is more nuanced and we should be precise about it:

- **During a live at-bat**, MLB Stats API updates within 5-15 seconds of the pitch
- **Our ingest** runs every 60 seconds during live games
- **Our SSE broadcast** delivers to connected clients within 100ms of the DB write
- **The split-flap animation** runs over 600ms

So the latency from "ball lands in the gap" to "the cell flips on your screen" is **15-90 seconds**, with most of that being the wait for the next ingest tick. That's "live enough" for a leaderboard — we're not making roster decisions in real time, we're showing trends.

The case study uses these exact numbers. "Live" is honest when defined this way; misleading when left vague.

If we wanted true sub-10-second updates, we'd have to use the MLB streaming API (a websocket feed that pushes pitch-by-pitch). That's a significant complexity bump and overkill for a leaderboard view. v1 stays with the polling model.
