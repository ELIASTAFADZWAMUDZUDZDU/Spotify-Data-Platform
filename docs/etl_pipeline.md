# Data Ingestion and ETL

Column-level mapping from the CSV to the schema is in [`data_mapping.md`](data_mapping.md). This page describes how the scripts run.

## Run order (from the project root)
1. `database/schema.sql` – create tables
2. `database/seed.sql` – insert the Free (`plan_id` 1) and Premium (`plan_id` 2) plans. **Run once**; the generator assumes these IDs.
3. `python -m scripts.load_spotify_data` – catalogue
4. `python -m scripts.generate_and_load_transaction_data` – synthetic users, playlists, listening history
5. `database/indexes.sql`, then `database/powerbi_views.sql`

## 1. Catalogue loader – `scripts/load_spotify_data.py`
**Extract:** reads `data/raw/spotify_tracks.csv` (114,000 rows; one row has no names and is skipped).
**Transform:**
- Splits the `artists` column on `;` and trims names → 29,858 distinct artist names in the file.
- Takes the **first** listed artist as the track's artist; creates an album per (album, artist) pair.
- Converts `duration_ms` to whole seconds.
- Replaces non-positive or missing `tempo` with NULL.
- Ignores Spotify's own `track_id` (PostgreSQL generates keys). The file has 89,741 distinct Spotify track IDs, so about 24k rows are the same track listed under several genres; each row is loaded as its own `track` row.

**Load:** `genre` → `artist` → `album` → `track`, using `ON CONFLICT DO NOTHING` for genres, artists and albums (re-runnable), but `track` inserts are **not** de-duplicated, so re-running adds duplicate tracks.
The genre step was added in this review: `seed.sql` only contains 10 generic genres that do not match the dataset's 114.

## 2. Synthetic data – `scripts/generate_and_load_transaction_data.py`
| Entity | Rule in code |
|---|---|
| Users | `NUM_USERS = 10000` attempts; Faker username/country; signup date within the last 5 years; 80 % Free / 20 % Premium; duplicate usernames skipped |
| Playlists | 70 % of users get 1–5 playlists, names drawn from a list of 20 |
| Playlist tracks | 20–100 random tracks per playlist |
| Listening history | 20–100 listens per user; track chosen uniformly at random; timestamp random within the last 2 years; duration between 30 % and 100 % of the track |

**Caveats:** the generator is not idempotent (each run adds playlists and listens for *all* users), inserts row by row (slow at this scale), and draws listen dates independently of signup dates.

## Validation
No data-quality checks run inside the scripts beyond the schema's constraints. Record counts are printed to the console.
After loading, sanity-check with simple counts (`SELECT COUNT(*) FROM track;` etc.).
