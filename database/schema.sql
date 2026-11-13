-- =========================================================
-- Spotify Data Platform - Core Schema
-- =========================================================


CREATE TABLE genre (
    genre_id SERIAL PRIMARY KEY,
    genre_name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE subscription_plan (
    plan_id BIGSERIAL PRIMARY KEY,
    plan_name VARCHAR(50) UNIQUE NOT NULL,
    monthly_price DECIMAL(6,2) NOT NULL,
    max_audio_quality VARCHAR(50) NOT NULL
);

CREATE TABLE artist (
    artist_id BIGSERIAL PRIMARY KEY,
    artist_name VARCHAR(200) UNIQUE NOT NULL,
    country VARCHAR(100)
);

CREATE TABLE album (
    album_id BIGSERIAL PRIMARY KEY,
    artist_id BIGINT NOT NULL,
    album_name TEXT NOT NULL,
    release_date DATE,

    CONSTRAINT fk_album_artist
        FOREIGN KEY (artist_id)
        REFERENCES artist(artist_id),

    CONSTRAINT uq_album_artist
        UNIQUE (album_name, artist_id)
);

CREATE TABLE track (
    track_id BIGSERIAL PRIMARY KEY,
    album_id BIGINT NOT NULL,
    genre_id BIGINT NOT NULL,

    track_name TEXT NOT NULL,

    duration_seconds INTEGER NOT NULL
        CHECK (duration_seconds > 0),

    popularity INTEGER
        CHECK (popularity BETWEEN 0 AND 100),

    danceability DECIMAL(4,3)
        CHECK (danceability BETWEEN 0 AND 1),

    energy DECIMAL(4,3)
        CHECK (energy BETWEEN 0 AND 1),

    valence DECIMAL(4,3)
        CHECK (valence BETWEEN 0 AND 1),

    tempo DECIMAL(6,2)
        CHECK (tempo > 0),

    CONSTRAINT fk_track_album
        FOREIGN KEY (album_id)
        REFERENCES album(album_id),

    CONSTRAINT fk_track_genre
        FOREIGN KEY (genre_id)
        REFERENCES genre(genre_id)
);

CREATE TABLE app_user (
    user_id BIGSERIAL PRIMARY KEY,

    username VARCHAR(100) UNIQUE NOT NULL,

    country VARCHAR(100),

    signup_date DATE NOT NULL,

    plan_id BIGINT NOT NULL,

    CONSTRAINT fk_user_plan
        FOREIGN KEY (plan_id)
        REFERENCES subscription_plan(plan_id)
);

CREATE TABLE playlist (
    playlist_id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL,

    playlist_name VARCHAR(200) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_playlist_user
        FOREIGN KEY (user_id)
        REFERENCES app_user(user_id)
);

CREATE TABLE playlist_track (

    playlist_id BIGINT NOT NULL,

    track_id BIGINT NOT NULL,

    added_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (playlist_id, track_id),

    CONSTRAINT fk_playlisttrack_playlist
        FOREIGN KEY (playlist_id)
        REFERENCES playlist(playlist_id),

    CONSTRAINT fk_playlisttrack_track
        FOREIGN KEY (track_id)
        REFERENCES track(track_id)
);

CREATE TABLE listening_history (

    listening_id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL,

    track_id BIGINT NOT NULL,

    listened_at TIMESTAMP NOT NULL,

    listening_duration INTEGER NOT NULL
        CHECK (listening_duration >= 0),

    CONSTRAINT fk_history_user
        FOREIGN KEY (user_id)
        REFERENCES app_user(user_id),

    CONSTRAINT fk_history_track
        FOREIGN KEY (track_id)
        REFERENCES track(track_id)
);
