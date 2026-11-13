
"""
Shared feature preparation for the ML modules.

PostgreSQL is the single source of track data.
"""

import pandas as pd


# Four numerical audio features used across our ML models.
NUMERIC_FEATURES = [
    "danceability",
    "energy",
    "valence",
    "tempo",
]

# Genre is used as a categorical input where appropriate.
CATEGORICAL_FEATURES = ["track_genre"]


def load_tracks(conn):
    """Load the track catalog from PostgreSQL."""

    if conn is None:
        raise ValueError("A PostgreSQL connection is required.")

    sql = """
        SELECT
            t.track_id,
            t.track_name,
            ar.artist_name,
            g.genre_name AS track_genre,
            t.popularity,
            t.duration_seconds,
            t.danceability,
            t.energy,
            t.valence,
            t.tempo
        FROM track t
        JOIN album al ON al.album_id = t.album_id
        JOIN artist ar ON ar.artist_id = al.artist_id
        JOIN genre g ON g.genre_id = t.genre_id;
    """

    df = pd.read_sql(sql, conn)

    if df.empty:
        raise ValueError("No tracks were returned from PostgreSQL.")

    required_columns = [
        "track_id",
        "track_name",
        "artist_name",
        "track_genre",
        "popularity",
        *NUMERIC_FEATURES,
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Track data is missing required columns: "
            + ", ".join(missing)
        )

    return df
