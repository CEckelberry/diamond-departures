CREATE TABLE teams (
    id          int PRIMARY KEY,
    abbr        varchar(3) NOT NULL UNIQUE,
    name        text NOT NULL,
    division    text NOT NULL,
    league      text NOT NULL,
    ballpark_id int
);

CREATE TABLE players (
    id              int PRIMARY KEY,
    full_name       text NOT NULL,
    short_name      text NOT NULL,
    bats            char(1) CHECK (bats IN ('L', 'R', 'S')),
    throws          char(1) CHECK (throws IN ('L', 'R', 'S')),
    primary_pos     varchar(3),
    eligible_pos    varchar(3)[] NOT NULL DEFAULT '{}',
    team_id         int REFERENCES teams(id),
    is_active       bool NOT NULL DEFAULT true,
    is_qualified    bool NOT NULL DEFAULT false,
    last_seen_at    timestamptz NOT NULL,
    headshot_url    text
);

CREATE TABLE player_stats (
    id          bigserial PRIMARY KEY,
    player_id   int NOT NULL REFERENCES players(id),
    stat_name   varchar(20) NOT NULL,
    stat_value  numeric(8, 3) NOT NULL,
    valid_from  timestamptz NOT NULL,
    valid_to    timestamptz,
    source      varchar(40) NOT NULL,
    season      int NOT NULL,
    sample_size int,
    CHECK (valid_to IS NULL OR valid_to > valid_from)
);

CREATE INDEX idx_player_stats_current ON player_stats (player_id, stat_name, season)
    WHERE valid_to IS NULL;

CREATE INDEX idx_player_stats_history ON player_stats (player_id, stat_name, valid_from);

CREATE TABLE leaderboard_views (
    id              bigserial PRIMARY KEY,
    view_key        varchar(40) NOT NULL,
    sort_stat       varchar(20) NOT NULL,
    rank            int NOT NULL CHECK (rank > 0),
    player_id       int NOT NULL REFERENCES players(id),
    stat_value      numeric(8, 3) NOT NULL,
    refreshed_at    timestamptz NOT NULL,
    UNIQUE (view_key, sort_stat, rank)
);

CREATE INDEX idx_leaderboard_views_lookup ON leaderboard_views (view_key, sort_stat, rank);

CREATE TABLE games (
    id                  int PRIMARY KEY,
    home_team           int NOT NULL REFERENCES teams(id),
    away_team           int NOT NULL REFERENCES teams(id),
    scheduled           timestamptz NOT NULL,
    state               varchar(20) NOT NULL,
    season              int NOT NULL,
    final_score_home    int,
    final_score_away    int,
    CHECK (state IN ('scheduled', 'live', 'final', 'postponed')),
    CHECK (home_team <> away_team)
);

CREATE INDEX idx_games_state ON games (state, scheduled DESC);

CREATE TABLE ingest_runs (
    id              bigserial PRIMARY KEY,
    started_at      timestamptz NOT NULL,
    completed_at    timestamptz,
    status          varchar(20) NOT NULL,
    games_processed int,
    stats_updated   int,
    error_message   text,
    schema_hash     varchar(64),
    CHECK (status IN ('running', 'success', 'failed', 'drift_detected')),
    CHECK (completed_at IS NULL OR completed_at >= started_at)
);
