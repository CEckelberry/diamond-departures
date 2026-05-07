# Design

The visual and interaction language for Diamond Departures. The split-flap aesthetic isn't a decorative choice — it's the project's identity. This document is mostly about getting it right.

---

## Design tension: nostalgia + clarity

The Penn Station / Frankfurt Hauptbahnhof split-flap board is one of the most iconic information displays of the 20th century. People know it instantly, even if they've never seen one in person — it's been imitated in every airport in the world. Using it as the visual frame for a leaderboard is a strong choice that comes with risk: if we lean too hard into the kitsch, the site looks like a novelty toy. If we lean too soft, we lose the thing that makes the project distinctive.

The right answer is to take the *mechanics* of the split-flap (flipping cells, mechanical timing, the rhythm of updates) seriously, while letting the *typography and layout* be modern. We're not trying to recreate a 1970s departure board pixel-for-pixel. We're using its DNA — the way information arrives, the way changes feel — in a contemporary frame.

The principles below are how we walk that line.

**1. The flip is sacred.** Every value change must flip. No fades, no slides, no number-counting up. The flip is what makes the project memorable, and it has to be everywhere a number changes.

**2. Stillness is OK.** A board full of constantly-flipping cells is exhausting. When nothing's changing, nothing should move. The split-flap mechanic earns its impact by being rare in any given second.

**3. Density without noise.** A leaderboard wants to show 100 rows × 5-6 columns. That's 500+ cells. Most of them are static at any moment. Visual hierarchy makes the 1-2 cells that just flipped instantly findable.

**4. Sound is a feature, not the default.** Real split-flaps clack. Reproducing the sound (gently) is right. Making it default-on isn't — it's a 60-second wait for the user to mute it. Default off, with a prominent toggle.

---

## Inherited tokens

The full token system from the portfolio's `DESIGN.md` is inherited:
- Palette structure (cotton-candy, light + dark modes)
- Typography (Inter / Instrument Serif / JetBrains Mono)
- Spacing scale, radii, easing, durations

What changes for Diamond is the *application* of those tokens. The split-flap's deep purple background is the dominant surface. JetBrains Mono is more prominent than on the portfolio (it's the natural typeface for stat values). The palette gets a few additional tokens specific to baseball:

### Diamond-specific tokens

| Token | Hex (dark) | Hex (light) | Use |
|---|---|---|---|
| `--board-bg` | `#0e0820` | `#1a0f3a` | Board frame background |
| `--cell-bg` | `#26215C` | `#1f1a4a` | Individual cell background |
| `--cell-edge` | `rgba(0,0,0,0.4)` | same | Cell hairline (the gap between flap halves) |
| `--cell-text` | `#FAC775` | `#FAC775` | The classic amber against deep purple |
| `--cell-text-dim` | `#9D7C49` | `#9D7C49` | Secondary text |
| `--rank-text` | `rgba(255,255,255,0.4)` | same | Position numbers |
| `--row-up` | `#5DCAA5` | `#5DCAA5` | Climbing direction indicator |
| `--row-down` | `#ED93B1` | `#ED93B1` | Falling direction indicator |
| `--row-new` | `#F4C0D1` | `#F4C0D1` | Just-qualified, just-called-up |

The amber-on-deep-purple is the project's signature. It's so iconic that we keep it in light mode too — the surrounding chrome adapts, but the board itself stays dark. A "light board" mode is technically possible but loses the project's identity.

---

## The split-flap mechanic

This is the main event. Getting this right is the difference between a memorable site and a forgettable one.

### Anatomy of a flap

Each cell in the board is a "flap unit": a fixed-width box (28px × 36px for digits, wider for letters) with text centered inside. The cell consists of two halves — top half showing the upper portion of the character, bottom half showing the lower portion — separated by a 1px black hairline.

```
┌──────────┐  ← top half
│          │
│    8     │  ← character spans both halves
│- - - - - │  ← hairline (--cell-edge)
│          │
│          │
└──────────┘  ← bottom half
```

When a cell's value changes, the animation runs in three phases:

**Phase 1 — Top flips down (200ms)**
The top half rotates around its bottom edge, falling forward. Behind it, the *new* character's top half is already painted. By the time the rotation reaches 90°, only the new character is visible above the hairline.

**Phase 2 — Brief pause (50ms)**
A single frame of stillness. This is what makes the mechanic feel mechanical — real flap displays have this pause as the next segment loads.

**Phase 3 — Bottom flips down (200ms)**
The bottom half (still showing the old character) rotates around its top edge, revealing the new character's bottom half behind it.

Total duration: **450ms**. Not 600ms (too slow, feels lazy), not 250ms (too fast, illegible). 450ms is the sweet spot from prototyping.

### The intermediate-character question

Real split-flap displays cycle through every character between the old and new. If the cell shows "8" and needs to display "5", a real board flips through 9 → 0 → 1 → 2 → 3 → 4 → 5. This takes seconds and is dramatic.

For our use case, full intermediate cycling is too slow. A leaderboard with 50 cells changing simultaneously and each taking 2 seconds becomes a 2-second freeze of nothing-readable. We use a **simplified mechanic**: each cell flips directly old → new in 450ms, with no intermediate characters.

We get the *feel* of a split-flap without the latency.

For occasional drama (the visitor switching the sort stat — a moment where a long animation is welcome), we have an optional "full cycle" mode that can be enabled in settings. Off by default. The case study can show it as a deliberate compromise.

### When a row changes rank

When a player's rank changes (e.g., they move from #5 to #2), the entire row slides vertically over 600ms with `--ease-out` cubic. During the slide:
- Other rows shift to make space (also animated, staggered by 30ms each so the eye can follow)
- The rank cell flips on every row whose number changed
- The stat cell that triggered the rank change flips simultaneously

If multiple rows change at once (a stat-picker switch causes 30 rows to reshuffle), the animation staggers by 50ms per affected row. The whole reshuffle takes ~3 seconds. That sounds long, but it's *the* visual — visitors will watch the entire animation play out, and shorter doesn't read as well.

### When a row appears or disappears

A new player qualifying for the leaderboard mid-game enters from the bottom — the row slides up from below the visible area, and a small "(new)" tag appears in the player name cell, fading out after 24 hours.

A player dropping off (e.g., placed on the IL) exits via fade-out over 1 second. The row position collapses smoothly.

### Reduced motion

`prefers-reduced-motion: reduce` swaps the flap animation for an instant value change with a brief background flash (200ms, the new value's color tinting the cell). Rank changes still happen but without the slide — rows just snap to new positions.

---

## Sound

Real split-flap displays make a satisfying clack. We replicate it carefully.

### The sounds

Three samples, all in the audio/ directory:
- `flap-single.mp3` — one cell's flip, ~50ms, soft mechanical clack
- `flap-many.mp3` — multiple cells flipping near-simultaneously, ~200ms
- `flap-row-shift.mp3` — paper-shuffle sound for row position changes

### When to play

- Single cell value change → `flap-single.mp3`
- Multiple cells changing within 100ms of each other → `flap-many.mp3` (one play, even if 30 cells changed)
- Row position changes → `flap-row-shift.mp3`

A debounce prevents sound stacking: if a sound is already playing, additional triggers within 100ms are skipped.

### Default state

**Sound off by default.** A small speaker icon in the upper-right toggles it. The toggle state persists in localStorage. First-time visitors see a brief tooltip near the icon: "Tap to hear it" — visible for 5 seconds, dismissable.

When sound is enabled, the volume defaults to 30% (split-flap clacks are surprisingly loud at full volume). A small volume slider next to the toggle lets the visitor tune it.

### Why sound matters here

Most websites with sound effects are annoying. Diamond is one of the rare cases where the sound is the experience. The mechanical clack is half the appeal of a real split-flap board. Without sound, we have a visual gimmick. With sound, we have an *instrument*.

Engineers will appreciate the restraint of having it default-off. Baseball nerds will turn it on and leave it on.

---

## Layout

The board is the visual centerpiece. Everything else exists to serve it.

### Page structure

```
┌────────────────────────────────────────────────────────────┐
│ NAV (back to portfolio · github · case study)              │
├────────────────────────────────────────────────────────────┤
│ HEADER                                                      │
│   Title: "Top hitters · sorted by wRC+"                    │
│   Status: live · 4 games in progress · 23 stats fresh      │
│   Sound: 🔊 [────●────]                                     │
├────────────────────────────────────────────────────────────┤
│ CONTROLS                                                    │
│   View tabs: All hitters · All pitchers · By position [▼] │
│   Stat picker: wRC+  wOBA  AVG  OBP  SLG  OPS  ISO  ...   │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  THE BOARD                                                  │
│                                                             │
│  RANK  PLAYER         TEAM   POS   wRC+   AVG   OBP   SLG │
│  ───── ────────────── ────── ───── ────── ───── ───── ─── │
│   01   Judge, A.      NYY    OF    198    .322  .429  .622│
│   02   Ohtani, S.     LAD    DH    186    .310  .412  .608│
│   03   Soto, J.       NYM    OF    172    .288  .398  .545│
│   04   Witt Jr., B.   KC     SS    168    .335  .389  .582│
│   05   Betts, M.      LAD    OF    154    .301  .380  .512│
│   ...                                                       │
│   (94 more rows)                                            │
│                                                             │
├────────────────────────────────────────────────────────────┤
│ FOOTER · methodology link · github · about                  │
└────────────────────────────────────────────────────────────┘
```

### Spacing and proportions

The board's width is constrained to ~960px on desktop. Wider feels like a spreadsheet; narrower hides columns we want visible. Below 960px the secondary stat columns drop off in priority order.

Row height: 36px. Tight enough to fit ~25 rows in viewport without scrolling. Loose enough that the flap animation has room.

Column proportions:
- Rank: 48px
- Player name: 200px (truncates with ellipsis on the rare long name)
- Team: 56px (3-letter abbr in mono)
- Position: 56px
- Stat columns: 80px each, monospace-aligned at the decimal

The first stat column (the active sort) is wider (96px) and tinted slightly to indicate which stat is doing the sorting.

### Responsive behavior

**Tablet (768-1024px):** The board narrows. Position column drops if needed; stat columns drop one at a time from the right. The active sort stat always stays visible.

**Mobile (< 768px):** The board becomes a vertical list of cards. Each row is a card showing rank, player name, the active sort stat, and the team. Other stats hidden behind a "details" tap. The split-flap mechanic still works on cards but row-shift becomes vertical instead of horizontal.

The mobile experience is intentionally simpler. The board's beauty is on desktop; on mobile we serve the data, not the spectacle.

---

## Components

### Header status bar

A horizontal row of status indicators just below the page title. Read in this order, left to right:

- **Mode pill**: "live" (teal, animated pulse) or "between games" (amber, static) or "off-season" (gray, static)
- **Game count**: "4 games in progress" with a tiny gameball icon
- **Freshness summary**: "23 stats fresh · 2 stale · 0 old"
- **Last update**: "23s ago"

Hovering any of these shows a tooltip with more detail. Clicking the freshness summary opens the freshness debugging panel (see Transparency below).

### Stat picker

A horizontal scrolling row of clickable stat labels. The active stat is highlighted (amber pill). Hovering shows the stat's full name and a one-line description ("wRC+ · weighted runs created plus, league-adjusted to 100").

Stats are grouped — hitting stats for the hitter views, pitching stats for the pitcher views. When the visitor switches to "All pitchers," the stat picker re-populates with pitching options.

### View tabs

Three top-level tabs: "All hitters", "All pitchers", "By position." The third tab opens a dropdown of position selections (C, 1B, 2B, ..., RP).

Active tab is solid; inactive tabs are outlined. Switching tabs triggers the same view-change animation as a stat picker change — the board reshuffles, every changed cell flips.

### Player detail modal

Opened by clicking any row in the board. A side-panel slide-in from the right (40% viewport width on desktop, full-width on mobile). Contains:

- **Header**: player headshot, full name, team, position, age
- **Hot stats**: the 6-8 most relevant stats for this player's role, displayed in larger split-flap cells
- **Full stat table**: a longer table of secondary stats, scrollable
- **Season trend**: a line chart of the currently-active stat over the season
- **Recent games**: a small table of the last 5 games' stat lines

Closing returns to the board. Browser back button works. The URL updates to `/player/judge-a` so the panel state is shareable.

### Freshness debugging panel

A nerd-mode panel that opens from the header status bar. Shows:
- Last 10 ingest runs with timestamps and outcomes
- Per-stat freshness (which stats were updated when)
- Source attribution per stat
- Schema-drift detection log

Engineers will read this. Recruiters won't notice it. That's correct.

---

## Color and visual hierarchy

The board is monochrome (amber-on-purple) by deliberate choice — that's the split-flap aesthetic. Color is reserved for *change indicators* and *interactive elements*:

- **Climbing indicators** (a row that just moved up): a teal arrow ▲ to the left of the rank, fades out over 5 seconds
- **Falling indicators** (just moved down): a pink arrow ▼, same fade
- **Just-qualified rows**: pink-soft tint on the row background, fades over 24 hours
- **Hover state**: the row's background lightens slightly (purple → slightly-lighter purple)
- **Click target**: the entire row, with a subtle hover-cue cursor change

This keeps the board itself reading as one coherent surface (the amber/purple) while making changes legible against it.

---

## Off-season presentation

When the site is in off-season mode, the board is essentially the same — same layout, same data — but with a few changes:

**The big banner.** Replaces the live status bar with: "**[Year] regular season · final**" in display type. Below it, a smaller line: "Next season starts in [N days]" with a countdown.

**No flips, no live updates.** Stats are final and won't change. SSE connection is not opened. The split-flap mechanic still works for stat-picker changes (because the data being re-sorted is real), just doesn't auto-flip from data updates.

**Preview mode toggle.** A button: "Preview mode · replay [date range]". Clicking starts a 5-minute accelerated replay of a recent week. Clearly labeled, can be exited at any time. Returns to the static final-season view.

The off-season presentation should not feel sad. It's a celebration of the season just ended. The display retains its dignity.

---

## Voice

The site's text voice carries from the portfolio: confident, plain, occasional dry humor, no marketing-speak. Specific patterns:

**Stat names are correct.** "wRC+" not "wRC plus" or "weighted runs". "K/9" not "K per 9". This is the correct vocabulary for the audience.

**Tooltips are educational, not dumbed-down.** "wRC+ measures total offensive contribution, league-adjusted so 100 is league average. Judge's 198 means 98% above average." Not "wRC+ is how good a hitter is."

**Mode messages are honest.** "No live games right now. Last updates from yesterday's games." Not "All caught up!" or vague chirpiness.

**Freshness language is precise.** "Updated 23 seconds ago" not "Live!" Numbers always present where verifiable.

**Honest framing of limits.** The about page or footer link to the data documentation explaining where stats come from and what they don't include. "This is computed from MLB Stats API and may differ slightly from FanGraphs in edge cases."

---

## Acceptance: what makes this site feel finished

Three tests:

**The 5-second test.** A new visitor lands on the page during a live game. Within 5 seconds, can they see (1) what the site shows, (2) the top player by the active stat, (3) that *something is happening*? If a cell hasn't visibly flipped within 5 seconds of load (assuming live games), the live aspect isn't being demonstrated.

**The animation test.** When the visitor switches the sort stat (e.g., wRC+ → OPS), the resulting board reshuffle should be the most beautiful 3 seconds on the site. Every cell that changed should flip. Every row that moved should slide. The eye should be able to follow what happened. If the reshuffle feels like a re-render rather than an animation, the project hasn't earned its premise.

**The nerd test.** A baseball nerd hovers over a specific stat cell. They see the source, the freshness, and the sample size. They click into a player detail; the formula and computation steps are accessible. If a curious fan can't verify our numbers, we don't have credibility.
