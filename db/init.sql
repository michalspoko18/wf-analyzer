-- wf-analyzer schema
-- DOW convention: 0 = Monday … 6 = Sunday (ISO weekday - 1)

CREATE TABLE IF NOT EXISTS gyms (
    id      SERIAL PRIMARY KEY,
    name    TEXT NOT NULL UNIQUE,
    address TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS gym_occupancy_samples (
    id           SERIAL PRIMARY KEY,
    gym_id       INTEGER      NOT NULL REFERENCES gyms (id),
    measured_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    people_count INTEGER      NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_samples_gym_time
    ON gym_occupancy_samples (gym_id, measured_at DESC);

CREATE TABLE IF NOT EXISTS gym_occupancy_hourly (
    gym_id        INTEGER NOT NULL REFERENCES gyms (id),
    dow           INTEGER NOT NULL CHECK (dow BETWEEN 0 AND 6),
    hour          INTEGER NOT NULL CHECK (hour BETWEEN 0 AND 23),
    avg_people    FLOAT   NOT NULL,
    min_people    INTEGER NOT NULL,
    max_people    INTEGER NOT NULL,
    samples_count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (gym_id, dow, hour)
);

CREATE TABLE IF NOT EXISTS gym_occupancy_daily (
    gym_id        INTEGER NOT NULL REFERENCES gyms (id),
    dow           INTEGER NOT NULL CHECK (dow BETWEEN 0 AND 6),
    avg_people    FLOAT   NOT NULL,
    min_people    INTEGER NOT NULL,
    max_people    INTEGER NOT NULL,
    peak_hour     INTEGER,
    samples_count INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (gym_id, dow)
);

CREATE TABLE IF NOT EXISTS weather_samples (
    id           SERIAL PRIMARY KEY,
    gym_id       INTEGER     NOT NULL REFERENCES gyms (id),
    measured_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    temperature  FLOAT       NOT NULL,
    rain         FLOAT       NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_weather_gym_time
    ON weather_samples (gym_id, measured_at DESC);

-- Seed: 3 monitored gyms
INSERT INTO gyms (name, address)
VALUES
    ('Stargard, Zachód',              'Szczecińska 45'),
    ('Szczecin, Hanza',               'Wyzwolenia 46'),
    ('Szczecin, Słoneczne Centrum',   'Andrzeja Struga 18')
ON CONFLICT (name) DO NOTHING;
