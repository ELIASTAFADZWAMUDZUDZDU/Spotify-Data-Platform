
"""
Content-based "similar tracks" recommender - the same idea behind
Spotify's own "Fans also like" / radio seeding.

Recommends similar tracks using audio features and genre.

Example:
python -m src.recommender.content_based --track "Blinding Lights" --n 5
"""

import argparse

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.neighbors import NearestNeighbors

from src.ml.feature_prep import (
    load_tracks,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
)

from src.config.database import get_connection


def prepare_features(tracks):
    """Prepare numerical and categorical features."""

    tracks = tracks.dropna(
        subset=NUMERIC_FEATURES + CATEGORICAL_FEATURES
    ).reset_index(drop=True)

    preprocessor = ColumnTransformer([
        ("numbers", StandardScaler(), NUMERIC_FEATURES),
        (
            "genre",
            OneHotEncoder(handle_unknown="ignore"),
            CATEGORICAL_FEATURES,
        ),
    ])

    features = preprocessor.fit_transform(tracks)

    return tracks, features


def train_recommender(features):
    """Fit the nearest-neighbour model."""

    model = NearestNeighbors(
        metric="cosine",
        algorithm="brute",
    )

    model.fit(features)

    return model


def recommend_songs(track_name, tracks, features, model, n=5, track_id=None):
    """
    Find tracks similar to the selected track.

    Track names are not unique in the catalogue, so callers that know the
    exact track (for example the Streamlit app) should pass ``track_id``.
    Without it, the first track with a matching name is used.
    """

    if track_id is not None:
        matches = tracks[tracks["track_id"] == track_id]
    else:
        matches = tracks[
            tracks["track_name"].str.lower() == track_name.lower()
        ]

    if matches.empty:
        raise ValueError(f"Track '{track_name}' was not found.")

    track_index = matches.index[0]

    n = min(n, len(tracks) - 1)

    if n < 1:
        raise ValueError("At least two tracks are required.")

    distances, indices = model.kneighbors(
        features[track_index:track_index + 1],
        n_neighbors=n + 1,
    )

    recommendations = tracks.iloc[indices[0]].copy()

    recommendations["similarity"] = 1 - distances[0]

    recommendations = recommendations[
        recommendations.index != track_index
    ]

    return recommendations.head(n)[
        ["track_name", "artist_name", "track_genre", "similarity"]
    ]


def main():
    """Run the recommendation system."""

    parser = argparse.ArgumentParser()

    parser.add_argument("--track", required=True)
    parser.add_argument("--n", type=int, default=5)

    args = parser.parse_args()

    conn = get_connection()

    try:
        tracks = load_tracks(conn)

        tracks, features = prepare_features(tracks)

        model = train_recommender(features)

        results = recommend_songs(
            args.track,
            tracks,
            features,
            model,
            args.n,
        )

        print(f"\nSongs similar to {args.track}:\n")
        print(results.to_string(index=False))

    finally:
        conn.close()


if __name__ == "__main__":
    main()
