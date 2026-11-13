# Data Mapping Document

## Purpose

This document describes how the raw Spotify dataset is mapped into the PostgreSQL database.

Rather than importing the CSV directly into a single table, the data is transformed into a normalized relational schema. This process preserves data integrity, eliminates redundancy, and prepares the database for analytics and machine learning.

---

# Source Dataset

Dataset: Spotify Tracks Dataset

Location:

data/raw/spotify_tracks.csv

---

# Mapping Strategy

| Dataset Column | Database Table | Database Column | Transformation | Reason |
|----------------|---------------|-----------------|---------------|--------|
| track_id | - | - | Ignore | PostgreSQL generates its own primary key. |
| artists | artist | artist_name | Extract primary artist | Avoid duplicate artist records. |
| album_name | album | album_name | None | Album entity. |
| track_name | track | track_name | None | Track entity. |
| popularity | track | popularity | None | Analytics and popularity ranking. |
| duration_ms | track | duration_seconds | Convert milliseconds to seconds | Easier for reporting and analysis. |
| explicit | track | explicit | None | Useful filtering attribute. |
| danceability | track | danceability | None | Recommendation feature. |
| energy | track | energy | None | Recommendation feature. |
| key | track | musical_key | Rename column | Avoid SQL reserved word confusion and improve readability. |
| loudness | track | loudness | None | Audio feature. |
| mode | track | mode | None | Audio feature. |
| speechiness | track | speechiness | None | Recommendation feature. |
| acousticness | track | acousticness | None | Recommendation feature. |
| instrumentalness | track | instrumentalness | None | Recommendation feature. |
| liveness | track | liveness | None | Recommendation feature. |
| valence | track | valence | None | Recommendation feature. |
| tempo | track | tempo | None | Analytics and recommendation feature. |
| time_signature | track | time_signature | None | Musical metadata. |
| track_genre | genre | genre_name | Remove duplicates | Normalize genres into a lookup table. |

---

# Normalization Decisions

## Artist

The raw dataset stores the artist name for every track.

Instead of repeating the artist name thousands of times, each artist will be stored once in the Artist table. Tracks reference artists indirectly through albums.

---

## Album

Albums are stored once.

Multiple tracks belonging to the same album reference the same album record.

---

## Genre

Genres are treated as reference data.

Duplicate genres are removed before insertion into the Genre table.

---

## Track

The Track table contains only attributes describing an individual song.

Foreign keys connect each track to its album and genre.

---

# Data Transformations

During loading, the following transformations will occur:

- Convert duration from milliseconds to seconds.
- Remove duplicate artists.
- Remove duplicate albums.
- Remove duplicate genres.
- Resolve foreign keys before inserting dependent tables.
- Ignore the original Spotify track identifier.

---

# Loading Order

Because of foreign key dependencies, tables must be populated in the following order:

1. Genre
2. SubscriptionPlan
3. Artist
4. Album
5. Track
6. User (synthetic)
7. Playlist (synthetic)
8. PlaylistTrack (synthetic)
9. ListeningHistory (synthetic)

This loading sequence ensures that every foreign key references an existing record.
