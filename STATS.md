# Stats

The sabermetric stat catalog. Every stat displayed on the site has an entry here with its formula, range, sample-size requirements, and "how to read it" notes.

This document is the source of truth for the `packages/stats/` library. When implementing a new stat, follow the entry here. When in doubt about a value, the formula here is what the implementation should match.

---

## Conventions

**Sample size.** Most rate stats are unstable in small samples. Each entry notes the minimum sample size where the stat starts to mean something. Below that minimum, the site shows the value but tags it `(unqualified)` and de-emphasizes the row.

**Park factors.** Some stats (ERA+, OPS+) include park-factor adjustments. We use the league-published park factors, refreshed annually. Specific factors live in `packages/content/park-factors-{year}.json`.

**League context.** Some stats are league-relative (wRC+, ERA+). The "league" for these is MLB-wide for current season, computed from all qualified hitters or pitchers respectively.

**Formula sources.** When a stat has multiple variants in the wild, we note which one we use. Generally we follow FanGraphs because that's what most fans recognize.

---

## Hitting stats

### AVG — Batting Average

**Formula:** `H / AB`

**Range:** ~.150 (terrible) to ~.380 (extraordinary). League average ~.245.

**Sample size:** Stabilizes around 250 plate appearances. Below that, AVG is mostly noise.

**How to read:** The oldest measure of hitting. Misleading in isolation because it ignores walks. Still on the site because casual fans know it.

### OBP — On-Base Percentage

**Formula:** `(H + BB + HBP) / (AB + BB + HBP + SF)`

**Range:** ~.250 (poor) to ~.420 (elite). League average ~.315.

**Sample size:** Stabilizes around 300 PA.

**How to read:** Better than AVG because it counts walks. A .300 OBP is poor; .400 is great.

### SLG — Slugging Percentage

**Formula:** `TB / AB` where `TB = 1B + 2*2B + 3*3B + 4*HR`

**Range:** ~.300 to ~.620.

**Sample size:** Stabilizes around 320 PA.

**How to read:** Total bases per at-bat. A .500 SLG means averaging a base every two ABs.

### OPS — On-Base Plus Slugging

**Formula:** `OBP + SLG`

**Range:** ~.600 to ~1.050.

**Sample size:** Same as its components.

**How to read:** A blunt but useful combination of getting on base and hitting for power. Limitation: it weights OBP and SLG equally, and they're not equally valuable. For a refined version, see wOBA.

### ISO — Isolated Power

**Formula:** `SLG - AVG`

**Range:** ~.080 to ~.300.

**Sample size:** Stabilizes around 350 PA.

**How to read:** Pure power measure. Strips out singles. .200 ISO is good; .250+ is elite power.

### BABIP — Batting Average on Balls in Play

**Formula:** `(H - HR) / (AB - K - HR + SF)`

**Range:** ~.250 to ~.350. League average ~.297.

**Sample size:** Highly variable. Doesn't fully stabilize until ~800 PA.

**How to read:** A noisy stat used as a "luck" indicator. A hitter with a .380 BABIP is probably running hot; .240 is probably running cold. Useful for projection, not for ranking.

**On the site:** We display BABIP but don't allow it as a primary sort for the leaderboard — it's too noisy to rank players by.

### wOBA — Weighted On-Base Average

**Formula:** `(0.69*BB + 0.72*HBP + 0.89*1B + 1.27*2B + 1.62*3B + 2.10*HR) / (AB + BB - IBB + SF + HBP)`

(Weights are from FanGraphs' annual context; updated yearly.)

**Range:** ~.290 to ~.430. League average ~.320.

**Sample size:** Stabilizes around 300 PA.

**How to read:** OPS done right — every hit type weighted by its actual run value. The fundamental modern rate stat. .350 is good; .400 is elite.

**Implementation note:** The weights drift annually with the run environment. We use the current-year weights from FanGraphs. The `packages/stats/woba-weights.json` file is updated each March before the season.

### wRC+ — Weighted Runs Created Plus

**Formula:** `100 * ((wOBA - lgwOBA) / wOBAScale + lgRuns/PA + (lgRuns/PA - PF * lgRuns/PA)) / (lgRuns/PA)`

(The classic FanGraphs formulation. wOBAScale is the multiplier that converts wOBA to runs. PF is the park factor.)

**Range:** Numbers are scaled so 100 = league average, 150 = 50% above average. Range ~50 (terrible) to ~200 (historic).

**Sample size:** Stabilizes around 300 PA.

**How to read:** The single best offensive stat for ranking. It accounts for everything wOBA does, plus park-adjusts. Judge at 198 means he created 98% more runs than the average hitter, accounting for the parks he played in.

**On the site:** This is the **default sort for hitters** because it's the gold standard for offense.

### Statcast: xBA, xSLG, xwOBA — Expected stats

**Formula:** Computed from Statcast batted-ball data (exit velocity, launch angle, sprint speed). Each batted ball is assigned an expected value based on a model trained on historical data, then summed.

**Range:** Similar to AVG/SLG/wOBA but typically less variance.

**Sample size:** Stabilizes faster than the actual stats — meaningful at ~150 batted balls.

**How to read:** What the player "should" be doing based on quality of contact, ignoring outcomes. Useful for spotting hitters running hot or cold. Their actual numbers will tend toward these over time.

**On the site:** Displayed in the player detail panel. Not on the main leaderboard at v1 (too niche for the default view).

---

## Pitching stats

### ERA — Earned Run Average

**Formula:** `(ER * 9) / IP`

**Range:** ~2.00 (elite) to ~5.50 (poor). League average ~4.10.

**Sample size:** Stabilizes around 100 IP for starters; ~50 for relievers.

**How to read:** The oldest pitching stat. Limited because it doesn't separate the pitcher's contribution from defense and luck. Still on the site for familiarity.

### WHIP — Walks + Hits per Innings Pitched

**Formula:** `(BB + H) / IP`

**Range:** ~0.95 (elite) to ~1.50 (poor).

**Sample size:** Same as ERA.

**How to read:** Traffic on base. 1.00 is great; 1.30 is league-ish.

### K/9 — Strikeouts per 9 Innings

**Formula:** `(K * 9) / IP`

**Range:** ~6.0 to ~13.0.

**Sample size:** Stabilizes around 70 IP.

**How to read:** A blunt rate of strikeout ability. K-BB% is more refined.

### BB/9 — Walks per 9 Innings

**Formula:** `(BB * 9) / IP`

**Range:** ~1.5 (elite control) to ~5.0 (wild).

**Sample size:** Stabilizes around 100 IP.

**How to read:** Walk rate. Lower is better. 2.0 is excellent; 4.0 is concerning.

### K-BB% — Strikeout minus Walk Percentage

**Formula:** `(K - BB) / TBF` where TBF is total batters faced

**Range:** ~5% to ~30%.

**Sample size:** Stabilizes around 70 IP. One of the fastest-stabilizing pitching stats.

**How to read:** The single most predictive pitching stat for future performance. 20% is excellent.

### FIP — Fielding Independent Pitching

**Formula:** `((13*HR + 3*(BB+HBP) - 2*K) / IP) + cFIP`

(cFIP is the league-adjustment constant, refreshed annually so league-average FIP equals league-average ERA.)

**Range:** Similar to ERA. ~2.50 elite, ~4.50 poor.

**Sample size:** Stabilizes faster than ERA — ~70 IP.

**How to read:** Defense-independent ERA. Strips out balls in play (which depend on the defense behind the pitcher). Better for evaluating pitcher skill in isolation.

**On the site:** This is the **default sort for pitchers**.

### xFIP — Expected FIP

**Formula:** Same as FIP but uses league-average HR/FB rate instead of the pitcher's actual HR allowed.

**Range:** Same as FIP.

**Sample size:** Same as FIP.

**How to read:** A second-derivative version of FIP that strips out HR variance. Useful but less popular than FIP. Pitchers with elevated HR/FB rates will have FIP > xFIP, suggesting regression.

### SIERA — Skill-Interactive ERA

**Formula:** A regression-based formula incorporating K%, BB%, GB%. Full formula in The Hardball Times' SIERA article (2010, refined since).

**Range:** Similar to ERA.

**Sample size:** ~70 IP.

**How to read:** The most sophisticated of the ERA-estimators. Accounts for batted-ball type (groundball pitchers fare better in SIERA than FIP). Some analysts prefer it; others prefer FIP. We display both.

### ERA+ — ERA Plus

**Formula:** `100 * (lgERA / ERA) * PF`

**Range:** Scaled so 100 = league average. 150+ is excellent.

**Sample size:** Same as ERA.

**How to read:** Park-adjusted, league-relative ERA. A pitcher with 150 ERA+ allowed 33% fewer earned runs than the league, adjusted for park.

---

## Defensive stats

These are the messiest part of the catalog. Defensive metrics have weaker theoretical foundations than offensive ones; small samples are very unreliable; and different methodologies give meaningfully different results.

### DRS — Defensive Runs Saved

**Source:** Computed by Sports Info Solutions, exposed via Baseball Savant.

**Range:** Roughly -25 (terrible) to +25 (Gold Glove caliber) over a full season.

**Sample size:** Use full-season values. Mid-season DRS is too noisy to rank by.

**How to read:** Runs saved compared to a league-average defender at the same position. +15 is excellent; -10 is concerning.

### UZR/150 — Ultimate Zone Rating, per 150 games

**Source:** FanGraphs (we'll mirror their methodology when computing locally).

**Range:** -20 to +20 per 150 games.

**Sample size:** Notoriously slow to stabilize — multiple full seasons recommended.

**How to read:** Similar to DRS but a different methodology. Comparing DRS and UZR for the same player is informative; if they agree, the player's defensive value is well-established.

**On the site:** We display UZR/150 but mark it `(noisy)` and don't allow it as a primary sort for sub-1000-inning samples.

### OAA — Outs Above Average

**Source:** Statcast tracking data.

**Range:** -15 to +15 over a full season.

**Sample size:** Stabilizes faster than DRS or UZR — meaningful at ~700 chances.

**How to read:** The most modern defensive metric. Based on real catch probabilities computed from tracking data.

**On the site:** Displayed for outfielders and infielders. Not available for catchers.

---

## Catcher-specific (omitted at v1)

Catcher defense involves framing, blocking, and throwing — three skills with different metrics. The leading framing metric (CSAA, Catcher Strike Probability Added) requires pitch-tracking data not exposed via free APIs.

**v1 decision:** We don't rank catchers by defensive value. The catcher leaderboard ranks by offensive contribution only (wRC+). The case study explains this honestly: catcher framing is a real and significant skill, but we don't have the data to measure it well.

**v2 stretch:** Add catcher framing if we can find a usable data source.

---

## Stats we don't include

To keep the catalog focused, several stats are omitted intentionally. The case study can mention these:

- **WAR** (Wins Above Replacement) — a single-number summary that's useful but contentious. Different frameworks (fWAR, bWAR, WARP) give different values. We display the components (offensive runs, defensive runs, etc.) without aggregating into WAR.
- **RBI** — a stat heavily influenced by teammates' on-base ability. Misleading as a measure of individual hitting.
- **Wins/Losses for pitchers** — a stat heavily influenced by run support. Misleading as a measure of pitching.
- **Saves** — a stat distorted by how managers use closers. Doesn't measure pitching skill cleanly.
- **Batting Average on the leaderboard's primary sort** — AVG is on the site but we don't lead with it because it's a poor ranking stat.

The choice not to include WAR is a deliberate one. WAR is genuinely informative when computed well, but the inputs (defensive metrics, positional adjustments, replacement-level baselines) involve enough subjectivity that we'd be re-deriving someone else's formula. We surface the components and let interested visitors aggregate them mentally.

---

## Position-specific defaults

Each position view has a default sort stat:

| Position | Default sort |
|---|---|
| Catcher | wRC+ (offense only — see catcher note) |
| 1B | wRC+ |
| 2B | wRC+ + DRS shown side-by-side |
| 3B | wRC+ + DRS |
| SS | wRC+ + OAA |
| LF | wRC+ |
| CF | wRC+ + OAA |
| RF | wRC+ |
| DH | wRC+ |
| SP | FIP |
| RP | K-BB% (more relevant than FIP for short-relief samples) |

These defaults can be changed by the visitor via the stat picker. The default reflects "if you had to pick one stat for this position, this is the most informative."

---

## Sample-size and qualification rules summary

| Role | Threshold for "qualified" | Threshold for "stat is meaningful" |
|---|---|---|
| Hitter | 2.7 PA per team game | 250+ PA |
| Starting pitcher | 1.0 IP per team game | 80+ IP |
| Reliever | 25 appearances | 25+ appearances |

Players below qualification:
- Don't appear on the main "All hitters" / "All pitchers" leaderboards
- Show in position-filtered views with `(unqualified)` tag
- Can still be reached via search and player-detail URLs

When a player crosses the qualification threshold mid-game, they appear on the main leaderboard with a `(just qualified)` badge for 24 hours. This is one of the more delightful animation moments — the row sliding in from below.
