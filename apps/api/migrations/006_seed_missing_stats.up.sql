-- Seed missing stat columns: wOBA, BABIP, ISO, BB%, K%, SB
-- Safe to re-run: guarded by WHERE NOT EXISTS on (player_id, stat_name, valid_to IS NULL)

INSERT INTO player_stats (player_id, stat_name, stat_value, valid_from, valid_to, source, season)
SELECT v.player_id, v.stat_name, v.stat_value, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026
FROM (VALUES
  -- Shohei Ohtani (elite all-around): wOBA, BABIP, ISO, BB%, K%, SB
  (1014,'wOBA', .418), (1014,'BABIP', .341), (1014,'ISO',  .342), (1014,'BB%', .138), (1014,'K%',  .187), (1014,'SB',  14),
  -- Aaron Stanton (power 1B)
  (1001,'wOBA', .390), (1001,'BABIP', .318), (1001,'ISO',  .297), (1001,'BB%', .116), (1001,'K%',  .215), (1001,'SB',   3),
  -- Marcus Devers (3B, balanced)
  (1002,'wOBA', .378), (1002,'BABIP', .325), (1002,'ISO',  .261), (1002,'BB%', .102), (1002,'K%',  .198), (1002,'SB',   5),
  -- Carlos Tatis (SS, tools)
  (1003,'wOBA', .360), (1003,'BABIP', .299), (1003,'ISO',  .267), (1003,'BB%', .095), (1003,'K%',  .228), (1003,'SB',  18),
  -- Dylan Trout (CF, well-rounded)
  (1004,'wOBA', .353), (1004,'BABIP', .312), (1004,'ISO',  .227), (1004,'BB%', .098), (1004,'K%',  .210), (1004,'SB',  11),
  -- Rafael Soto (2B, contact)
  (1005,'wOBA', .348), (1005,'BABIP', .308), (1005,'ISO',  .226), (1005,'BB%', .091), (1005,'K%',  .205), (1005,'SB',   8),
  -- Josh Alvarez (DH, slugger)
  (1006,'wOBA', .345), (1006,'BABIP', .283), (1006,'ISO',  .242), (1006,'BB%', .094), (1006,'K%',  .235), (1006,'SB',   2),
  -- Freddie Acuña (RF, tools)
  (1007,'wOBA', .373), (1007,'BABIP', .316), (1007,'ISO',  .260), (1007,'BB%', .100), (1007,'K%',  .220), (1007,'SB',  20),
  -- Manny Harper (LF)
  (1008,'wOBA', .366), (1008,'BABIP', .308), (1008,'ISO',  .252), (1008,'BB%', .105), (1008,'K%',  .225), (1008,'SB',   6),
  -- Pete Guerrero (1B)
  (1009,'wOBA', .356), (1009,'BABIP', .311), (1009,'ISO',  .239), (1009,'BB%', .097), (1009,'K%',  .218), (1009,'SB',   3),
  -- Corey Bogaerts (SS)
  (1010,'wOBA', .333), (1010,'BABIP', .289), (1010,'ISO',  .218), (1010,'BB%', .092), (1010,'K%',  .222), (1010,'SB',   7),
  -- Vladimir Judge (DH, big power)
  (1011,'wOBA', .368), (1011,'BABIP', .294), (1011,'ISO',  .268), (1011,'BB%', .110), (1011,'K%',  .245), (1011,'SB',   1),
  -- Julio Bregman (3B, patient)
  (1012,'wOBA', .350), (1012,'BABIP', .300), (1012,'ISO',  .242), (1012,'BB%', .104), (1012,'K%',  .198), (1012,'SB',   4),
  -- Bo Lindor (SS)
  (1013,'wOBA', .344), (1013,'BABIP', .292), (1013,'ISO',  .263), (1013,'BB%', .094), (1013,'K%',  .224), (1013,'SB',  14),
  -- Trea Swanson (SS, speedster)
  (1015,'wOBA', .332), (1015,'BABIP', .317), (1015,'ISO',  .209), (1015,'BB%', .071), (1015,'K%',  .186), (1015,'SB',  28),
  -- Yordan Ramirez (LF)
  (1016,'wOBA', .371), (1016,'BABIP', .321), (1016,'ISO',  .233), (1016,'BB%', .108), (1016,'K%',  .210), (1016,'SB',   2),
  -- Xander Turner (2B)
  (1017,'wOBA', .342), (1017,'BABIP', .305), (1017,'ISO',  .226), (1017,'BB%', .086), (1017,'K%',  .216), (1017,'SB',  12),
  -- Jose Arenado (3B)
  (1018,'wOBA', .339), (1018,'BABIP', .298), (1018,'ISO',  .231), (1018,'BB%', .085), (1018,'K%',  .220), (1018,'SB',   3),
  -- Alex Betts (RF)
  (1019,'wOBA', .343), (1019,'BABIP', .300), (1019,'ISO',  .226), (1019,'BB%', .098), (1019,'K%',  .218), (1019,'SB',   9),
  -- Nolan Machado (3B)
  (1020,'wOBA', .338), (1020,'BABIP', .283), (1020,'ISO',  .253), (1020,'BB%', .088), (1020,'K%',  .228), (1020,'SB',   4),
  -- Adley Rodriguez (C)
  (1021,'wOBA', .334), (1021,'BABIP', .298), (1021,'ISO',  .219), (1021,'BB%', .086), (1021,'K%',  .215), (1021,'SB',   2),
  -- Will Smith Jr. (C)
  (1022,'wOBA', .328), (1022,'BABIP', .282), (1022,'ISO',  .219), (1022,'BB%', .089), (1022,'K%',  .222), (1022,'SB',   1),
  -- Steven Vlad Jr. (1B, power)
  (1023,'wOBA', .332), (1023,'BABIP', .286), (1023,'ISO',  .236), (1023,'BB%', .077), (1023,'K%',  .238), (1023,'SB',   1),
  -- Giancarlo Cruz (1B, true power)
  (1024,'wOBA', .330), (1024,'BABIP', .267), (1024,'ISO',  .242), (1024,'BB%', .095), (1024,'K%',  .268), (1024,'SB',   0),
  -- Kyle Tucker (RF)
  (1025,'wOBA', .335), (1025,'BABIP', .285), (1025,'ISO',  .236), (1025,'BB%', .089), (1025,'K%',  .225), (1025,'SB',  10),
  -- Ronald Goldschmidt (1B)
  (1026,'wOBA', .340), (1026,'BABIP', .291), (1026,'ISO',  .223), (1026,'BB%', .107), (1026,'K%',  .220), (1026,'SB',   6),
  -- Juan Yelich (LF, contact)
  (1027,'wOBA', .337), (1027,'BABIP', .322), (1027,'ISO',  .196), (1027,'BB%', .090), (1027,'K%',  .185), (1027,'SB',  13),
  -- Bryce Cronenworth (2B)
  (1028,'wOBA', .323), (1028,'BABIP', .282), (1028,'ISO',  .205), (1028,'BB%', .082), (1028,'K%',  .226), (1028,'SB',   7),
  -- Austin Riley (3B)
  (1029,'wOBA', .326), (1029,'BABIP', .278), (1029,'ISO',  .239), (1029,'BB%', .087), (1029,'K%',  .240), (1029,'SB',   2),
  -- Salvador Realmuto (C)
  (1030,'wOBA', .321), (1030,'BABIP', .276), (1030,'ISO',  .230), (1030,'BB%', .088), (1030,'K%',  .238), (1030,'SB',   8),
  -- Luis Arraez (elite contact, high AVG, low power, low K)
  (1031,'wOBA', .368), (1031,'BABIP', .352), (1031,'ISO',  .061), (1031,'BB%', .076), (1031,'K%',  .062), (1031,'SB',   3),
  -- Max Muncy (1B, patient, power)
  (1032,'wOBA', .336), (1032,'BABIP', .264), (1032,'ISO',  .218), (1032,'BB%', .132), (1032,'K%',  .258), (1032,'SB',   1),
  -- Tommy Edman (2B, speed)
  (1033,'wOBA', .311), (1033,'BABIP', .299), (1033,'ISO',  .197), (1033,'BB%', .072), (1033,'K%',  .195), (1033,'SB',  22),
  -- Ozzie Albies (2B, speed)
  (1034,'wOBA', .318), (1034,'BABIP', .302), (1034,'ISO',  .216), (1034,'BB%', .071), (1034,'K%',  .208), (1034,'SB',  17),
  -- Ha-Seong Kim (SS)
  (1035,'wOBA', .314), (1035,'BABIP', .296), (1035,'ISO',  .205), (1035,'BB%', .079), (1035,'K%',  .213), (1035,'SB',  15),
  -- Ian Happ (LF, patient)
  (1036,'wOBA', .323), (1036,'BABIP', .280), (1036,'ISO',  .213), (1036,'BB%', .108), (1036,'K%',  .245), (1036,'SB',   5),
  -- Nathaniel Lowe (1B)
  (1037,'wOBA', .315), (1037,'BABIP', .287), (1037,'ISO',  .187), (1037,'BB%', .094), (1037,'K%',  .215), (1037,'SB',   3),
  -- Willy Adames (SS)
  (1038,'wOBA', .309), (1038,'BABIP', .278), (1038,'ISO',  .209), (1038,'BB%', .085), (1038,'K%',  .248), (1038,'SB',   6),
  -- Jeimer Candelario (3B)
  (1039,'wOBA', .302), (1039,'BABIP', .273), (1039,'ISO',  .198), (1039,'BB%', .082), (1039,'K%',  .235), (1039,'SB',   2),
  -- Chas McCormick (CF)
  (1040,'wOBA', .295), (1040,'BABIP', .270), (1040,'ISO',  .191), (1040,'BB%', .078), (1040,'K%',  .242), (1040,'SB',   9)
) AS v(player_id, stat_name, stat_value)
WHERE NOT EXISTS (
    SELECT 1 FROM player_stats ps
    WHERE ps.player_id = v.player_id
      AND ps.stat_name = v.stat_name
      AND ps.valid_to IS NULL
);

-- Leaderboard views for the new sort stats: wOBA, ISO, BABIP, SB, BB%, K%

-- hitters by wOBA
INSERT INTO leaderboard_views (view_key, sort_stat, rank, player_id, stat_value, refreshed_at)
SELECT
    'hitters' AS view_key,
    'wOBA'    AS sort_stat,
    ROW_NUMBER() OVER (ORDER BY ps.stat_value DESC) AS rank,
    ps.player_id,
    ps.stat_value,
    NOW()     AS refreshed_at
FROM player_stats ps
WHERE ps.stat_name = 'wOBA' AND ps.valid_to IS NULL
ON CONFLICT (view_key, sort_stat, rank) DO UPDATE SET
    player_id    = EXCLUDED.player_id,
    stat_value   = EXCLUDED.stat_value,
    refreshed_at = EXCLUDED.refreshed_at;

-- hitters by ISO
INSERT INTO leaderboard_views (view_key, sort_stat, rank, player_id, stat_value, refreshed_at)
SELECT
    'hitters' AS view_key,
    'ISO'     AS sort_stat,
    ROW_NUMBER() OVER (ORDER BY ps.stat_value DESC) AS rank,
    ps.player_id,
    ps.stat_value,
    NOW()     AS refreshed_at
FROM player_stats ps
WHERE ps.stat_name = 'ISO' AND ps.valid_to IS NULL
ON CONFLICT (view_key, sort_stat, rank) DO UPDATE SET
    player_id    = EXCLUDED.player_id,
    stat_value   = EXCLUDED.stat_value,
    refreshed_at = EXCLUDED.refreshed_at;

-- hitters by BABIP
INSERT INTO leaderboard_views (view_key, sort_stat, rank, player_id, stat_value, refreshed_at)
SELECT
    'hitters' AS view_key,
    'BABIP'   AS sort_stat,
    ROW_NUMBER() OVER (ORDER BY ps.stat_value DESC) AS rank,
    ps.player_id,
    ps.stat_value,
    NOW()     AS refreshed_at
FROM player_stats ps
WHERE ps.stat_name = 'BABIP' AND ps.valid_to IS NULL
ON CONFLICT (view_key, sort_stat, rank) DO UPDATE SET
    player_id    = EXCLUDED.player_id,
    stat_value   = EXCLUDED.stat_value,
    refreshed_at = EXCLUDED.refreshed_at;

-- hitters by SB
INSERT INTO leaderboard_views (view_key, sort_stat, rank, player_id, stat_value, refreshed_at)
SELECT
    'hitters' AS view_key,
    'SB'      AS sort_stat,
    ROW_NUMBER() OVER (ORDER BY ps.stat_value DESC) AS rank,
    ps.player_id,
    ps.stat_value,
    NOW()     AS refreshed_at
FROM player_stats ps
WHERE ps.stat_name = 'SB' AND ps.valid_to IS NULL
ON CONFLICT (view_key, sort_stat, rank) DO UPDATE SET
    player_id    = EXCLUDED.player_id,
    stat_value   = EXCLUDED.stat_value,
    refreshed_at = EXCLUDED.refreshed_at;

-- hitters by BB%
INSERT INTO leaderboard_views (view_key, sort_stat, rank, player_id, stat_value, refreshed_at)
SELECT
    'hitters' AS view_key,
    'BB%'     AS sort_stat,
    ROW_NUMBER() OVER (ORDER BY ps.stat_value DESC) AS rank,
    ps.player_id,
    ps.stat_value,
    NOW()     AS refreshed_at
FROM player_stats ps
WHERE ps.stat_name = 'BB%' AND ps.valid_to IS NULL
ON CONFLICT (view_key, sort_stat, rank) DO UPDATE SET
    player_id    = EXCLUDED.player_id,
    stat_value   = EXCLUDED.stat_value,
    refreshed_at = EXCLUDED.refreshed_at;

-- hitters by K%
INSERT INTO leaderboard_views (view_key, sort_stat, rank, player_id, stat_value, refreshed_at)
SELECT
    'hitters' AS view_key,
    'K%'      AS sort_stat,
    ROW_NUMBER() OVER (ORDER BY ps.stat_value DESC) AS rank,
    ps.player_id,
    ps.stat_value,
    NOW()     AS refreshed_at
FROM player_stats ps
WHERE ps.stat_name = 'K%' AND ps.valid_to IS NULL
ON CONFLICT (view_key, sort_stat, rank) DO UPDATE SET
    player_id    = EXCLUDED.player_id,
    stat_value   = EXCLUDED.stat_value,
    refreshed_at = EXCLUDED.refreshed_at;
