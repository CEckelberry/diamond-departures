# Diamond Departures

> Top 100 active MLB players ranked by sabermetrics, styled as a Penn Station split-flap board, updated live during games.

**Status:** ⚪ Concept · not started yet · case study at [cole-eckelberry.com/work/diamond](https://cole-eckelberry.com/work/diamond)

## The pitch

There's a specific aesthetic — the old Penn Station / Frankfurt Hauptbahnhof split-flap departure boards — where the letters and numbers physically rotate when they change. It's iconic. It feels alive in a way an LCD display doesn't. A leaderboard styled like that, ranking the top 100 active MLB players by advanced sabermetrics and updating live as games progress, is a visual nobody has built and a sports nerd's dream.

Mid-game: a player gets a hit, his wRC+ shifts, his rank changes, the affected rows physically flip to their new values. Players climbing get a green up-arrow that flashes; players dropping get a red down-arrow.

## What it shows

The default landing tab is wRC+ for hitters — the single best "who is the best hitter in baseball right now" stat. Every other stat category is a tab.

**Hitters.** AVG, OBP, SLG, OPS, wRC+, wOBA, BABIP, ISO, fWAR, plus the traditionals (TB, RBI, R) for completeness.

**Pitchers.** ERA, FIP, xFIP, SIERA, ERA+, K/9, BB/9, K-BB%, WHIP, fWAR.

**Defensive.** DRS by position, UZR/150 for outfielders and infielders, OAA where available.

**Position views.** A tab per position (C, 1B, 2B, 3B, SS, LF, CF, RF, DH, SP, RP) showing the top players at that position by the most-relevant stat (wRC+ for hitters, FIP for pitchers, framing runs for catchers).

## The board

Amber monospace on deep purple. When a value changes, the cell rotates upward, exits the top, and the new value rotates in from the bottom. ~600 ms per flip; subtle "click click click" SFX, off by default. When a player changes rank, the entire row slides up or down to its new position with the same flap animation on every column. Multiple simultaneous changes stagger by 50 ms so the eye can follow.

## Live updates

The Go backend ingests data from a sports-stats provider every 30 seconds during active games. It diffs the latest snapshot against the previous one, computes which leaderboards moved, and broadcasts only the deltas — not the full board — to subscribed clients via Server-Sent Events. The frontend animates only the cells that changed.

Off-game-time (off-hours, off-season), the board updates from cached data and only changes when daily aggregate stats roll over. There's a "season summary" mode for the off-season so the page isn't dead from November through February.

## Tech stack (planned)

- **Frontend:** SvelteKit, TypeScript, Tailwind v4
- **Backend:** Go (`chi` + custom SSE implementation)
- **Database:** Postgres for the player roster + cached stat history
- **Stats provider:** MLB Stats API (free) at v1, with a small derived-stats layer (compute wRC+ from raw events). Swap in paid Sportradar later if traffic justifies.
- **Hosting:** Cloud Run for both the frontend and the Go backend; Cloud SQL Postgres.

## Open design questions

- Historical mode ("show me top 100 by wRC+ from 2019"). v2 trap; defer until asked for repeatedly.
- Sharing: a static-image generator so people can post "my favorite SS leaderboard right now" — Open Graph image generation that captures the live state.
- Notifications: ping me when a chosen player's rank changes by more than N positions. Needs a user model — defer.

## Privacy

Repo is private during development; will go public when there's something to show.

## Related

- Portfolio site: [cole-resume-website](https://github.com/CEckelberry/cole-resume-website)
- Infra: [portfolio-iac](https://github.com/CEckelberry/portfolio-iac)
