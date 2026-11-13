
"""
Popularity Predictor

Predicts track popularity using four audio features and genre.
"""

from pathlib import Path

import joblib

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.ml.feature_prep import (
    load_tracks,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
)


ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"

TEST_SIZE = 0.2
RANDOM_STATE = 42


def build_pipeline():
    """Create the preprocessing and prediction pipeline."""

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "genre",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_FEATURES,
            ),
        ],
        remainder="passthrough",
    )

    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=12,
        min_samples_leaf=5,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model),
    ])

    return pipeline


def train(conn, save=True):
    """Train and evaluate the popularity predictor."""

    df = load_tracks(conn)

    required_columns = (
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
        + ["popularity"]
    )

    df = df.dropna(subset=required_columns).copy()

    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df["popularity"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    pipeline = build_pipeline()

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    print("\nPOPULARITY PREDICTOR RESULTS")
    print("----------------------------")
    print(f"Training tracks: {len(X_train):,}")
    print(f"Testing tracks: {len(X_test):,}")
    print(f"Mean Absolute Error: {mae:.2f}")
    print(f"R² Score: {r2:.4f}")

    if save:
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

        joblib.dump(
            pipeline,
            ARTIFACT_DIR / "popularity_model.joblib",
        )

        print(f"\nModel saved to: {ARTIFACT_DIR}")

    return pipeline


def predict_popularity(pipeline, danceability, energy, valence, tempo, genre):
    """Predict popularity for one track."""

    import pandas as pd

    track = pd.DataFrame([{
        "danceability": danceability,
        "energy": energy,
        "valence": valence,
        "tempo": tempo,
        "track_genre": genre,
    }])

    return float(pipeline.predict(track)[0])


def main():
    """Train the popularity predictor from the PostgreSQL catalogue."""

    from src.config.database import get_connection

    conn = get_connection()

    try:
        train(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
