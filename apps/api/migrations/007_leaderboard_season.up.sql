ALTER TABLE leaderboard_views ADD COLUMN season int NOT NULL DEFAULT 2026;

ALTER TABLE leaderboard_views
    DROP CONSTRAINT leaderboard_views_view_key_sort_stat_rank_key;

ALTER TABLE leaderboard_views
    ADD CONSTRAINT leaderboard_views_view_key_sort_stat_season_rank_key
    UNIQUE (view_key, sort_stat, season, rank);

DROP INDEX IF EXISTS idx_leaderboard_views_lookup;
CREATE INDEX idx_leaderboard_views_lookup
    ON leaderboard_views (view_key, sort_stat, season, rank);
