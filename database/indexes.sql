-- =========================================================
-- Indexes to support the analytics queries in
-- src/analytics/queries.py and the Streamlit dashboard.
-- Run after schema.sql + data load.
-- =========================================================

-- listening_history is the biggest, most-queried table:
-- almost every analytics question filters/groups by these.
CREATE INDEX IF NOT EXISTS idx_history_user_id     ON listening_history(user_id);
CREATE INDEX IF NOT EXISTS idx_history_track_id    ON listening_history(track_id);
CREATE INDEX IF NOT EXISTS idx_history_listened_at ON listening_history(listened_at);

-- track lookups by genre/album (genre breakdowns, catalog joins)
CREATE INDEX IF NOT EXISTS idx_track_genre_id ON track(genre_id);
CREATE INDEX IF NOT EXISTS idx_track_album_id ON track(album_id);

-- album -> artist rollups (top artists queries)
CREATE INDEX IF NOT EXISTS idx_album_artist_id ON album(artist_id);

-- user cohort / plan analytics
CREATE INDEX IF NOT EXISTS idx_user_plan_id     ON app_user(plan_id);
CREATE INDEX IF NOT EXISTS idx_user_signup_date ON app_user(signup_date);

-- playlist analytics
CREATE INDEX IF NOT EXISTS idx_playlist_user_id       ON playlist(user_id);
CREATE INDEX IF NOT EXISTS idx_playlisttrack_track_id ON playlist_track(track_id);
