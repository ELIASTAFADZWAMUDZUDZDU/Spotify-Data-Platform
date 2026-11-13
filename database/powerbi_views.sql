-- =========================================================
-- Reporting views for Power BI (star schema)
-- Run after schema.sql, indexes.sql, views.sql and the data load:
--   psql -d <database> -f database/powerbi_views.sql
--
-- Power BI works best with one fact table (one row per event)
-- surrounded by small dimension tables. These views provide that:
--
--   bi_dim_plan ---< bi_dim_user ---< bi_fact_listening >--- bi_dim_track
--
-- The date table is created inside Power BI (see docs/powerbi.md).
-- =========================================================

CREATE OR REPLACE VIEW bi_dim_plan AS
SELECT
    plan_id,
    plan_name,
    monthly_price,
    max_audio_quality
FROM subscription_plan;


-- One row per user. activated_30d = 1 if the user listened at least once
-- within 30 days after signing up (same idea as signup_cohort_retention
-- in src/analytics/queries.py, but counting only listens after signup).
CREATE OR REPLACE VIEW bi_dim_user AS
SELECT
    u.user_id,
    u.username,
    u.country,
    u.signup_date,
    DATE_TRUNC('month', u.signup_date)::date AS signup_month,
    u.plan_id,
    sp.plan_name,
    CASE
        WHEN EXISTS (
            SELECT 1
            FROM listening_history lh
            WHERE lh.user_id = u.user_id
              AND lh.listened_at >= u.signup_date
              AND lh.listened_at <= u.signup_date + INTERVAL '30 days'
        ) THEN 1 ELSE 0
    END AS activated_30d
FROM app_user u
JOIN subscription_plan sp ON sp.plan_id = u.plan_id;


-- One row per track, with album, artist and genre attached.
CREATE OR REPLACE VIEW bi_dim_track AS
SELECT
    t.track_id,
    t.track_name,
    ar.artist_name,
    al.album_name,
    al.release_date,
    g.genre_name,
    t.popularity,
    t.duration_seconds,
    t.danceability,
    t.energy,
    t.valence,
    t.tempo
FROM track t
JOIN album  al ON al.album_id  = t.album_id
JOIN artist ar ON ar.artist_id = al.artist_id
JOIN genre  g  ON g.genre_id   = t.genre_id;


-- One row per listen. is_likely_skip uses the same rule as vw_listening_enriched:
-- the user heard less than 35% of the track.
CREATE OR REPLACE VIEW bi_fact_listening AS
SELECT
    lh.listening_id,
    lh.user_id,
    lh.track_id,
    lh.listened_at,
    lh.listened_at::date AS listen_date,
    lh.listening_duration,
    LEAST(1.0, lh.listening_duration::NUMERIC / NULLIF(t.duration_seconds, 0)) AS completion_rate,
    CASE
        WHEN lh.listening_duration::NUMERIC / NULLIF(t.duration_seconds, 0) < 0.35 THEN 1
        ELSE 0
    END AS is_likely_skip
FROM listening_history lh
JOIN track t ON t.track_id = lh.track_id;
