"""Unit tests for the ML components using a small synthetic catalogue.

They do not need PostgreSQL. The recommender test is skipped if psycopg2
is not installed (src.config.database imports it).
"""

import unittest

import numpy as np
import pandas as pd

from src.ml.popularity_model import build_pipeline, predict_popularity
from src.ml.feature_prep import NUMERIC_FEATURES, CATEGORICAL_FEATURES


def make_tracks(n=200, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "track_id": np.arange(1, n + 1),
        "track_name": [f"Song {i % 150}" for i in range(n)],  # duplicate names
        "artist_name": [f"Artist {i % 20}" for i in range(n)],
        "track_genre": rng.choice(["pop", "rock", "jazz"], n),
        "popularity": rng.integers(0, 100, n),
        "danceability": rng.random(n),
        "energy": rng.random(n),
        "valence": rng.random(n),
        "tempo": rng.uniform(60, 200, n),
    })


class PopularityModelTests(unittest.TestCase):

    def test_pipeline_fits_and_predicts(self):
        df = make_tracks()
        X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
        pipeline = build_pipeline().fit(X, df["popularity"])
        value = predict_popularity(pipeline, 0.5, 0.6, 0.4, 120, "pop")
        self.assertIsInstance(value, float)
        self.assertTrue(0 <= value <= 100)

    def test_unseen_genre_is_handled(self):
        df = make_tracks()
        X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
        pipeline = build_pipeline().fit(X, df["popularity"])
        value = predict_popularity(pipeline, 0.5, 0.6, 0.4, 120, "unseen-genre")
        self.assertTrue(np.isfinite(value))


class RecommenderTests(unittest.TestCase):

    def setUp(self):
        try:
            from src.recommender import content_based
        except ImportError as error:  # psycopg2 missing
            self.skipTest(str(error))
        self.cb = content_based
        self.tracks, self.features = content_based.prepare_features(make_tracks())
        self.model = content_based.train_recommender(self.features)

    def test_returns_requested_number_and_excludes_seed(self):
        result = self.cb.recommend_songs(
            "Song 3", self.tracks, self.features, self.model, n=5
        )
        self.assertEqual(len(result), 5)
        self.assertEqual(
            list(result.columns),
            ["track_name", "artist_name", "track_genre", "similarity"],
        )

    def test_track_id_selects_the_exact_duplicate(self):
        # "Song 3" exists twice (ids 4 and 154); ask for the second one.
        by_name = self.cb.recommend_songs(
            "Song 3", self.tracks, self.features, self.model, n=5
        )
        by_id = self.cb.recommend_songs(
            "Song 3", self.tracks, self.features, self.model, n=5, track_id=154
        )
        self.assertNotEqual(list(by_name.index), list(by_id.index))
        self.assertNotIn(153, by_id.index)  # the seed row itself is excluded

    def test_unknown_track_raises(self):
        with self.assertRaises(ValueError):
            self.cb.recommend_songs(
                "No such song", self.tracks, self.features, self.model
            )


if __name__ == "__main__":
    unittest.main()
