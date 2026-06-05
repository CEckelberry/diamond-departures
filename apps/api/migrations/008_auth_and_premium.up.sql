CREATE TABLE users (
    id           uuid PRIMARY KEY,
    email        text NOT NULL UNIQUE,
    name         text,
    avatar_url   text,
    is_premium   bool NOT NULL DEFAULT false,
    purchased_at timestamptz,
    created_at   timestamptz NOT NULL DEFAULT now(),
    last_seen_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE watch_boards (
    id         uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id    uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name       text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE watch_board_players (
    board_id  uuid NOT NULL REFERENCES watch_boards(id) ON DELETE CASCADE,
    player_id int  NOT NULL REFERENCES players(id)      ON DELETE CASCADE,
    added_at  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (board_id, player_id)
);

CREATE TABLE watchlist_players (
    user_id   uuid NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
    player_id int  NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    added_at  timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, player_id)
);

CREATE TABLE email_alerts (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       uuid NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
    player_id     int  NOT NULL REFERENCES players(id) ON DELETE CASCADE,
    stat_name     varchar(20) NOT NULL,
    threshold     numeric(8,3) NOT NULL,
    direction     varchar(4) NOT NULL CHECK (direction IN ('up', 'down')),
    last_fired_at timestamptz,
    created_at    timestamptz NOT NULL DEFAULT now()
);
