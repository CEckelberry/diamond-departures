CREATE TABLE drift_signatures (
    id              bigserial PRIMARY KEY,
    source_key      varchar(80) NOT NULL,
    signature       varchar(64) NOT NULL,
    observed_at     timestamptz NOT NULL DEFAULT now(),
    is_current      bool NOT NULL DEFAULT true,
    parse_error     bool NOT NULL DEFAULT false,
    UNIQUE (source_key, signature)
);

CREATE INDEX idx_drift_signatures_current
    ON drift_signatures (source_key, observed_at DESC)
    WHERE is_current = true;
