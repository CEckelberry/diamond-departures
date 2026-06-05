-- Demo player + stat seed so the board has data to display.
-- All names, IDs, and numbers are fictional.

INSERT INTO players (id, full_name, short_name, primary_pos, eligible_pos, team_id, last_seen_at, headshot_url) VALUES
  (1001, 'Aaron Stanton',    'A. Stanton',  '1B',  ARRAY['1B'],        147, NOW(), NULL),
  (1002, 'Marcus Devers',    'M. Devers',   '3B',  ARRAY['3B'],        111, NOW(), NULL),
  (1003, 'Carlos Tatis',     'C. Tatis',    'SS',  ARRAY['SS'],        135, NOW(), NULL),
  (1004, 'Dylan Trout',      'D. Trout',    'CF',  ARRAY['CF','OF'],   108, NOW(), NULL),
  (1005, 'Rafael Soto',      'R. Soto',     '2B',  ARRAY['2B'],        119, NOW(), NULL),
  (1006, 'Josh Alvarez',     'J. Alvarez',  'DH',  ARRAY['DH'],        117, NOW(), NULL),
  (1007, 'Freddie Acuña',    'F. Acuña',    'RF',  ARRAY['RF','OF'],   144, NOW(), NULL),
  (1008, 'Manny Harper',     'M. Harper',   'LF',  ARRAY['LF','OF'],   143, NOW(), NULL),
  (1009, 'Pete Guerrero',    'P. Guerrero', '1B',  ARRAY['1B'],        119, NOW(), NULL),
  (1010, 'Corey Bogaerts',   'C. Bogaerts', 'SS',  ARRAY['SS'],        135, NOW(), NULL),
  (1011, 'Vladimir Judge',   'V. Judge',    'DH',  ARRAY['DH'],        147, NOW(), NULL),
  (1012, 'Julio Bregman',    'J. Bregman',  '3B',  ARRAY['3B'],        117, NOW(), NULL),
  (1013, 'Bo Lindor',        'B. Lindor',   'SS',  ARRAY['SS'],        121, NOW(), NULL),
  (1014, 'Shohei Ohtani',    'S. Ohtani',   'DH',  ARRAY['DH'],        119, NOW(), NULL),
  (1015, 'Trea Swanson',     'T. Swanson',  'SS',  ARRAY['SS'],        112, NOW(), NULL),
  (1016, 'Yordan Ramirez',   'Y. Ramirez',  'LF',  ARRAY['LF','OF'],   117, NOW(), NULL),
  (1017, 'Xander Turner',    'X. Turner',   '2B',  ARRAY['2B'],        119, NOW(), NULL),
  (1018, 'Jose Arenado',     'J. Arenado',  '3B',  ARRAY['3B'],        138, NOW(), NULL),
  (1019, 'Alex Betts',       'A. Betts',    'RF',  ARRAY['RF','OF'],   119, NOW(), NULL),
  (1020, 'Nolan Machado',    'N. Machado',  '3B',  ARRAY['3B'],        135, NOW(), NULL),
  (1021, 'Adley Rodriguez',  'A. Rodriguez','C',   ARRAY['C'],         110, NOW(), NULL),
  (1022, 'Will Smith Jr.',   'W. Smith',    'C',   ARRAY['C'],         119, NOW(), NULL),
  (1023, 'Steven Vlad Jr.',  'S. Vlad Jr.', '1B',  ARRAY['1B'],        141, NOW(), NULL),
  (1024, 'Giancarlo Cruz',   'G. Cruz',     '1B',  ARRAY['1B'],        136, NOW(), NULL),
  (1025, 'Kyle Tucker',      'K. Tucker',   'RF',  ARRAY['RF','OF'],   112, NOW(), NULL),
  (1026, 'Ronald Goldschmidt','R. Goldy',   '1B',  ARRAY['1B'],        144, NOW(), NULL),
  (1027, 'Juan Yelich',      'J. Yelich',   'LF',  ARRAY['LF','OF'],   158, NOW(), NULL),
  (1028, 'Bryce Cronenworth','B. Cronen.',  '2B',  ARRAY['2B'],        135, NOW(), NULL),
  (1029, 'Austin Riley',     'A. Riley',    '3B',  ARRAY['3B'],        144, NOW(), NULL),
  (1030, 'Salvador Realmuto','S. Realmuto', 'C',   ARRAY['C'],         143, NOW(), NULL),
  (1031, 'Luis Arraez',      'L. Arraez',   '2B',  ARRAY['2B'],        146, NOW(), NULL),
  (1032, 'Max Muncy',        'M. Muncy',    '1B',  ARRAY['1B','2B'],   119, NOW(), NULL),
  (1033, 'Tommy Edman',      'T. Edman',    '2B',  ARRAY['2B','SS'],   119, NOW(), NULL),
  (1034, 'Ozzie Albies',     'O. Albies',   '2B',  ARRAY['2B'],        144, NOW(), NULL),
  (1035, 'Ha-Seong Kim',     'H. Kim',      'SS',  ARRAY['SS','2B'],   135, NOW(), NULL),
  (1036, 'Ian Happ',         'I. Happ',     'LF',  ARRAY['LF','OF'],   112, NOW(), NULL),
  (1037, 'Nathaniel Lowe',   'N. Lowe',     '1B',  ARRAY['1B'],        140, NOW(), NULL),
  (1038, 'Willy Adames',     'W. Adames',   'SS',  ARRAY['SS'],        158, NOW(), NULL),
  (1039, 'Jeimer Candelario','J. Candelario','3B', ARRAY['3B'],        113, NOW(), NULL),
  (1040, 'Chas McCormick',   'C. McCormick','CF',  ARRAY['CF','OF'],   117, NOW(), NULL)
ON CONFLICT (id) DO NOTHING;

-- Season stats for each player (valid_to IS NULL = current)
INSERT INTO player_stats (player_id, stat_name, stat_value, valid_from, valid_to, source, season) VALUES
  -- Shohei Ohtani (elite)
  (1014,'AVG',  .312, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1014,'OBP',  .413, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1014,'SLG',  .654, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1014,'OPS',  1.067,NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1014,'wRC+', 185,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1014,'HR',   22,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1014,'RBI',  61,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Aaron Stanton
  (1001,'AVG',  .294, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1001,'OBP',  .385, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1001,'SLG',  .591, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1001,'OPS',  .976, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1001,'wRC+', 162,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1001,'HR',   18,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1001,'RBI',  53,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Marcus Devers
  (1002,'AVG',  .301, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1002,'OBP',  .378, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1002,'SLG',  .562, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1002,'OPS',  .940, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1002,'wRC+', 155,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1002,'HR',   15,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1002,'RBI',  48,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Freddie Acuña
  (1007,'AVG',  .288, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1007,'OBP',  .371, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1007,'SLG',  .548, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1007,'OPS',  .919, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1007,'wRC+', 149,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1007,'HR',   14,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1007,'RBI',  45,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Yordan Ramirez
  (1016,'AVG',  .296, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1016,'OBP',  .387, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1016,'SLG',  .529, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1016,'OPS',  .916, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1016,'wRC+', 148,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1016,'HR',   13,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1016,'RBI',  50,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Vladimir Judge
  (1011,'AVG',  .276, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1011,'OBP',  .368, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1011,'SLG',  .544, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1011,'OPS',  .912, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1011,'wRC+', 146,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1011,'HR',   19,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1011,'RBI',  55,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Manny Harper
  (1008,'AVG',  .279, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1008,'OBP',  .374, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1008,'SLG',  .531, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1008,'OPS',  .905, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1008,'wRC+', 143,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1008,'HR',   16,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1008,'RBI',  47,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Pete Guerrero
  (1009,'AVG',  .285, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1009,'OBP',  .369, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1009,'SLG',  .524, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1009,'OPS',  .893, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1009,'wRC+', 140,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1009,'HR',   12,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1009,'RBI',  44,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Carlos Tatis
  (1003,'AVG',  .271, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1003,'OBP',  .352, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1003,'SLG',  .538, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1003,'OPS',  .890, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1003,'wRC+', 138,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1003,'HR',   17,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1003,'RBI',  46,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Bo Lindor
  (1013,'AVG',  .268, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1013,'OBP',  .349, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1013,'SLG',  .531, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1013,'OPS',  .880, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1013,'wRC+', 136,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1013,'HR',   14,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1013,'RBI',  42,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Julio Bregman
  (1012,'AVG',  .274, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1012,'OBP',  .362, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1012,'SLG',  .516, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1012,'OPS',  .878, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1012,'wRC+', 134,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1012,'HR',   11,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1012,'RBI',  41,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Dylan Trout
  (1004,'AVG',  .283, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1004,'OBP',  .360, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1004,'SLG',  .510, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1004,'OPS',  .870, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1004,'wRC+', 132,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1004,'HR',   10,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1004,'RBI',  38,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Rafael Soto
  (1005,'AVG',  .282, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1005,'OBP',  .356, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1005,'SLG',  .508, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1005,'OPS',  .864, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1005,'wRC+', 130,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1005,'HR',   9,    NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1005,'RBI',  37,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Josh Alvarez
  (1006,'AVG',  .265, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1006,'OBP',  .353, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1006,'SLG',  .507, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1006,'OPS',  .860, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1006,'wRC+', 128,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1006,'HR',   13,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1006,'RBI',  43,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Nolan Machado
  (1020,'AVG',  .261, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1020,'OBP',  .344, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1020,'SLG',  .514, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1020,'OPS',  .858, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1020,'wRC+', 127,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1020,'HR',   15,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1020,'RBI',  44,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Xander Turner
  (1017,'AVG',  .278, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1017,'OBP',  .348, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1017,'SLG',  .504, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1017,'OPS',  .852, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1017,'wRC+', 125,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1017,'HR',   10,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1017,'RBI',  36,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Alex Betts
  (1019,'AVG',  .271, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1019,'OBP',  .353, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1019,'SLG',  .497, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1019,'OPS',  .850, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1019,'wRC+', 124,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1019,'HR',   9,    NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1019,'RBI',  34,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Ronald Goldschmidt
  (1026,'AVG',  .266, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1026,'OBP',  .358, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1026,'SLG',  .489, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1026,'OPS',  .847, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1026,'wRC+', 122,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1026,'HR',   11,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1026,'RBI',  40,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Kyle Tucker
  (1025,'AVG',  .263, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1025,'OBP',  .345, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1025,'SLG',  .499, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1025,'OPS',  .844, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1025,'wRC+', 121,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1025,'HR',   12,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1025,'RBI',  39,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Jose Arenado
  (1018,'AVG',  .269, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1018,'OBP',  .341, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1018,'SLG',  .500, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1018,'OPS',  .841, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1018,'wRC+', 120,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1018,'HR',   13,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1018,'RBI',  41,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Juan Yelich
  (1027,'AVG',  .287, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1027,'OBP',  .356, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1027,'SLG',  .483, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1027,'OPS',  .839, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1027,'wRC+', 119,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1027,'HR',   7,    NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1027,'RBI',  32,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Austin Riley
  (1029,'AVG',  .259, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1029,'OBP',  .338, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1029,'SLG',  .498, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1029,'OPS',  .836, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1029,'wRC+', 118,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1029,'HR',   14,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1029,'RBI',  43,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Steven Vlad Jr.
  (1023,'AVG',  .267, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1023,'OBP',  .332, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1023,'SLG',  .503, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1023,'OPS',  .835, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1023,'wRC+', 117,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1023,'HR',   16,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1023,'RBI',  45,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Adley Rodriguez
  (1021,'AVG',  .272, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1021,'OBP',  .340, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1021,'SLG',  .491, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1021,'OPS',  .831, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1021,'wRC+', 116,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1021,'HR',   10,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1021,'RBI',  35,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Trea Swanson
  (1015,'AVG',  .280, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1015,'OBP',  .337, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1015,'SLG',  .489, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1015,'OPS',  .826, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1015,'wRC+', 114,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1015,'HR',   7,    NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1015,'RBI',  30,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Salvador Realmuto
  (1030,'AVG',  .258, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1030,'OBP',  .335, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1030,'SLG',  .488, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1030,'OPS',  .823, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1030,'wRC+', 113,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1030,'HR',   11,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1030,'RBI',  37,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Ozzie Albies
  (1034,'AVG',  .274, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1034,'OBP',  .330, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1034,'SLG',  .490, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1034,'OPS',  .820, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1034,'wRC+', 112,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1034,'HR',   9,    NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1034,'RBI',  33,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Corey Bogaerts
  (1010,'AVG',  .262, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1010,'OBP',  .338, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1010,'SLG',  .480, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1010,'OPS',  .818, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1010,'wRC+', 111,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1010,'HR',   8,    NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1010,'RBI',  31,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Will Smith Jr.
  (1022,'AVG',  .258, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1022,'OBP',  .336, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1022,'SLG',  .477, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1022,'OPS',  .813, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1022,'wRC+', 110,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1022,'HR',   9,    NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1022,'RBI',  32,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Ha-Seong Kim
  (1035,'AVG',  .270, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1035,'OBP',  .334, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1035,'SLG',  .475, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1035,'OPS',  .809, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1035,'wRC+', 108,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1035,'HR',   7,    NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1035,'RBI',  28,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Ian Happ
  (1036,'AVG',  .254, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1036,'OBP',  .340, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1036,'SLG',  .467, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1036,'OPS',  .807, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1036,'wRC+', 107,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1036,'HR',   8,    NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1036,'RBI',  30,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Giancarlo Cruz
  (1024,'AVG',  .245, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1024,'OBP',  .328, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1024,'SLG',  .487, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1024,'OPS',  .815, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1024,'wRC+', 115,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1024,'HR',   17,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1024,'RBI',  48,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Tommy Edman
  (1033,'AVG',  .265, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1033,'OBP',  .325, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1033,'SLG',  .462, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1033,'OPS',  .787, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1033,'wRC+', 102,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1033,'HR',   5,    NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1033,'RBI',  24,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Willy Adames
  (1038,'AVG',  .251, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1038,'OBP',  .322, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1038,'SLG',  .460, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1038,'OPS',  .782, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1038,'wRC+', 100,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1038,'HR',   9,    NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1038,'RBI',  31,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Luis Arraez
  (1031,'AVG',  .342, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1031,'OBP',  .395, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1031,'SLG',  .403, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1031,'OPS',  .798, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1031,'wRC+', 109,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1031,'HR',   2,    NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1031,'RBI',  22,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Bryce Cronenworth
  (1028,'AVG',  .253, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1028,'OBP',  .320, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1028,'SLG',  .458, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1028,'OPS',  .778, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1028,'wRC+', 98,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1028,'HR',   8,    NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1028,'RBI',  28,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Nathaniel Lowe
  (1037,'AVG',  .257, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1037,'OBP',  .330, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1037,'SLG',  .444, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1037,'OPS',  .774, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1037,'wRC+', 96,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1037,'HR',   7,    NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1037,'RBI',  27,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Max Muncy
  (1032,'AVG',  .234, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1032,'OBP',  .345, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1032,'SLG',  .452, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1032,'OPS',  .797, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1032,'wRC+', 106,  NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1032,'HR',   10,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1032,'RBI',  33,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Jeimer Candelario
  (1039,'AVG',  .248, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1039,'OBP',  .316, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1039,'SLG',  .446, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1039,'OPS',  .762, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1039,'wRC+', 93,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1039,'HR',   8,    NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1039,'RBI',  26,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  -- Chas McCormick
  (1040,'AVG',  .244, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1040,'OBP',  .312, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1040,'SLG',  .435, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1040,'OPS',  .747, NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1040,'wRC+', 88,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1040,'HR',   5,    NOW()-INTERVAL '1 hour', NULL, 'seed', 2026),
  (1040,'RBI',  21,   NOW()-INTERVAL '1 hour', NULL, 'seed', 2026)
ON CONFLICT DO NOTHING;

-- Populate leaderboard_views for hitters sorted by OPS and wRC+
-- (these are the two stats the API VALID_SORTS will most commonly receive)

-- hitters by OPS
INSERT INTO leaderboard_views (view_key, sort_stat, rank, player_id, stat_value, refreshed_at)
SELECT
    'hitters' AS view_key,
    'OPS'     AS sort_stat,
    ROW_NUMBER() OVER (ORDER BY ps.stat_value DESC) AS rank,
    ps.player_id,
    ps.stat_value,
    NOW()     AS refreshed_at
FROM player_stats ps
WHERE ps.stat_name = 'OPS' AND ps.valid_to IS NULL
ON CONFLICT (view_key, sort_stat, rank) DO UPDATE SET
    player_id    = EXCLUDED.player_id,
    stat_value   = EXCLUDED.stat_value,
    refreshed_at = EXCLUDED.refreshed_at;

-- hitters by wRC+
INSERT INTO leaderboard_views (view_key, sort_stat, rank, player_id, stat_value, refreshed_at)
SELECT
    'hitters' AS view_key,
    'wRC+'    AS sort_stat,
    ROW_NUMBER() OVER (ORDER BY ps.stat_value DESC) AS rank,
    ps.player_id,
    ps.stat_value,
    NOW()     AS refreshed_at
FROM player_stats ps
WHERE ps.stat_name = 'wRC+' AND ps.valid_to IS NULL
ON CONFLICT (view_key, sort_stat, rank) DO UPDATE SET
    player_id    = EXCLUDED.player_id,
    stat_value   = EXCLUDED.stat_value,
    refreshed_at = EXCLUDED.refreshed_at;

-- hitters by AVG
INSERT INTO leaderboard_views (view_key, sort_stat, rank, player_id, stat_value, refreshed_at)
SELECT
    'hitters' AS view_key,
    'AVG'     AS sort_stat,
    ROW_NUMBER() OVER (ORDER BY ps.stat_value DESC) AS rank,
    ps.player_id,
    ps.stat_value,
    NOW()     AS refreshed_at
FROM player_stats ps
WHERE ps.stat_name = 'AVG' AND ps.valid_to IS NULL
ON CONFLICT (view_key, sort_stat, rank) DO UPDATE SET
    player_id    = EXCLUDED.player_id,
    stat_value   = EXCLUDED.stat_value,
    refreshed_at = EXCLUDED.refreshed_at;

-- hitters by HR
INSERT INTO leaderboard_views (view_key, sort_stat, rank, player_id, stat_value, refreshed_at)
SELECT
    'hitters' AS view_key,
    'HR'      AS sort_stat,
    ROW_NUMBER() OVER (ORDER BY ps.stat_value DESC) AS rank,
    ps.player_id,
    ps.stat_value,
    NOW()     AS refreshed_at
FROM player_stats ps
WHERE ps.stat_name = 'HR' AND ps.valid_to IS NULL
ON CONFLICT (view_key, sort_stat, rank) DO UPDATE SET
    player_id    = EXCLUDED.player_id,
    stat_value   = EXCLUDED.stat_value,
    refreshed_at = EXCLUDED.refreshed_at;

-- hitters by RBI
INSERT INTO leaderboard_views (view_key, sort_stat, rank, player_id, stat_value, refreshed_at)
SELECT
    'hitters' AS view_key,
    'RBI'     AS sort_stat,
    ROW_NUMBER() OVER (ORDER BY ps.stat_value DESC) AS rank,
    ps.player_id,
    ps.stat_value,
    NOW()     AS refreshed_at
FROM player_stats ps
WHERE ps.stat_name = 'RBI' AND ps.valid_to IS NULL
ON CONFLICT (view_key, sort_stat, rank) DO UPDATE SET
    player_id    = EXCLUDED.player_id,
    stat_value   = EXCLUDED.stat_value,
    refreshed_at = EXCLUDED.refreshed_at;

-- hitters by SLG
INSERT INTO leaderboard_views (view_key, sort_stat, rank, player_id, stat_value, refreshed_at)
SELECT
    'hitters' AS view_key,
    'SLG'     AS sort_stat,
    ROW_NUMBER() OVER (ORDER BY ps.stat_value DESC) AS rank,
    ps.player_id,
    ps.stat_value,
    NOW()     AS refreshed_at
FROM player_stats ps
WHERE ps.stat_name = 'SLG' AND ps.valid_to IS NULL
ON CONFLICT (view_key, sort_stat, rank) DO UPDATE SET
    player_id    = EXCLUDED.player_id,
    stat_value   = EXCLUDED.stat_value,
    refreshed_at = EXCLUDED.refreshed_at;
