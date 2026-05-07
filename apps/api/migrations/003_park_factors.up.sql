CREATE TABLE park_factors (
    team_id     int NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    season      int NOT NULL,
    park_factor numeric(8, 3) NOT NULL,
    source      varchar(40) NOT NULL,
    updated_at  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (team_id, season)
);

CREATE INDEX idx_park_factors_season ON park_factors (season);

INSERT INTO park_factors (team_id, season, park_factor, source) VALUES
    (108, 2026, 1.004, 'manual:park-factors-2026'),
    (109, 2026, 1.005, 'manual:park-factors-2026'),
    (110, 2026, 0.999, 'manual:park-factors-2026'),
    (111, 2026, 1.013, 'manual:park-factors-2026'),
    (112, 2026, 1.001, 'manual:park-factors-2026'),
    (113, 2026, 1.017, 'manual:park-factors-2026'),
    (114, 2026, 0.995, 'manual:park-factors-2026'),
    (115, 2026, 1.118, 'manual:park-factors-2026'),
    (116, 2026, 0.995, 'manual:park-factors-2026'),
    (117, 2026, 0.993, 'manual:park-factors-2026'),
    (118, 2026, 1.004, 'manual:park-factors-2026'),
    (119, 2026, 0.952, 'manual:park-factors-2026'),
    (120, 2026, 0.967, 'manual:park-factors-2026'),
    (121, 2026, 0.994, 'manual:park-factors-2026'),
    (133, 2026, 1.035, 'manual:park-factors-2026'),
    (134, 2026, 0.986, 'manual:park-factors-2026'),
    (135, 2026, 0.968, 'manual:park-factors-2026'),
    (136, 2026, 0.930, 'manual:park-factors-2026'),
    (137, 2026, 0.946, 'manual:park-factors-2026'),
    (138, 2026, 0.957, 'manual:park-factors-2026'),
    (139, 2026, 0.971, 'manual:park-factors-2026'),
    (140, 2026, 1.019, 'manual:park-factors-2026'),
    (141, 2026, 1.002, 'manual:park-factors-2026'),
    (142, 2026, 0.998, 'manual:park-factors-2026'),
    (143, 2026, 1.011, 'manual:park-factors-2026'),
    (144, 2026, 1.008, 'manual:park-factors-2026'),
    (145, 2026, 1.028, 'manual:park-factors-2026'),
    (146, 2026, 0.960, 'manual:park-factors-2026'),
    (147, 2026, 0.978, 'manual:park-factors-2026'),
    (158, 2026, 1.018, 'manual:park-factors-2026')
ON CONFLICT (team_id, season) DO UPDATE
SET
    park_factor = EXCLUDED.park_factor,
    source = EXCLUDED.source,
    updated_at = now();
