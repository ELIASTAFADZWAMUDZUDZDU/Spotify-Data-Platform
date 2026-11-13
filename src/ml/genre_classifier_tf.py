
"""
Genre Classifier

Predicts a track's genre using four numerical audio features.

Run through a Python script that supplies a PostgreSQL connection.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score,
    top_k_accuracy_score,
    confusion_matrix,
)

from src.ml.feature_prep import load_tracks, NUMERIC_FEATURES


TOP_N_GENRES = 15
EPOCHS = 25
TEST_SIZE = 0.2
RANDOM_STATE = 42

ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"


def prepare_data(conn):
    """Load tracks and prepare four features and genre labels."""

    df = load_tracks(conn)

    df = df.dropna(
        subset=NUMERIC_FEATURES + ["track_genre"]
    ).copy()

    # Keep the 15 most common genres.
    top_genres = (
        df["track_genre"]
        .value_counts()
        .head(TOP_N_GENRES)
        .index
    )

    df = df[df["track_genre"].isin(top_genres)].reset_index(drop=True)

    X = df[NUMERIC_FEATURES].to_numpy()
    y_raw = df["track_genre"].to_numpy()

    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)

    return X, y, label_encoder


def build_model(number_of_genres):
    """Create the neural network."""

    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(len(NUMERIC_FEATURES),)),

        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dropout(0.2),

        tf.keras.layers.Dense(16, activation="relu"),

        tf.keras.layers.Dense(
            number_of_genres,
            activation="softmax"
        ),
    ])

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model


def train(conn, save=True):
    """Train and evaluate the genre classifier."""

    X, y, label_encoder = prepare_data(conn)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    # Fit the scaler on training data only.
    scaler = StandardScaler()

    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    model = build_model(len(label_encoder.classes_))

    model.fit(
        X_train,
        y_train,
        epochs=EPOCHS,
        batch_size=32,
        validation_split=0.2,
        verbose=1,
    )

    probabilities = model.predict(X_test, verbose=0)
    predictions = np.argmax(probabilities, axis=1)

    accuracy = accuracy_score(y_test, predictions)

    top_3_accuracy = top_k_accuracy_score(
        y_test,
        probabilities,
        k=3,
        labels=np.arange(len(label_encoder.classes_)),
    )

    # Generate the confusion matrix.
    cm = confusion_matrix(
        y_test,
        predictions,
        labels=np.arange(len(label_encoder.classes_)),
    )

    cm_df = pd.DataFrame(
        cm,
        index=label_encoder.classes_,
        columns=label_encoder.classes_,
    )

    print("\nGENRE CLASSIFIER RESULTS")
    print("------------------------")
    print(f"Number of genres: {len(label_encoder.classes_)}")
    print(f"Training tracks: {len(X_train):,}")
    print(f"Testing tracks: {len(X_test):,}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Top-3 accuracy: {top_3_accuracy:.4f}")

    print("\nCONFUSION MATRIX")
    print("----------------")
    print(cm_df.to_string())

    if save:
        ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

        model.save(ARTIFACT_DIR / "genre_classifier.keras")
        joblib.dump(scaler, ARTIFACT_DIR / "genre_scaler.joblib")
        joblib.dump(
            label_encoder,
            ARTIFACT_DIR / "genre_label_encoder.joblib",
        )

        print(f"\nModel artifacts saved to: {ARTIFACT_DIR}")

    return model, scaler, label_encoder


def predict_genre(model, scaler, label_encoder, features):
    """
    Predict a genre from four values in this order:
    danceability, energy, valence, tempo.
    """

    features = np.asarray(features, dtype=float).reshape(1, -1)

    if features.shape[1] != len(NUMERIC_FEATURES):
        raise ValueError(
            f"Expected {len(NUMERIC_FEATURES)} features: "
            + ", ".join(NUMERIC_FEATURES)
        )

    features = scaler.transform(features)

    probabilities = model.predict(features, verbose=0)[0]
    predicted_index = np.argmax(probabilities)

    return {
        "genre": label_encoder.inverse_transform(
            [predicted_index]
        )[0],
        "confidence": float(probabilities[predicted_index]),
    }


def main():
    """Train the genre classifier from the PostgreSQL catalogue."""

    from src.config.database import get_connection

    conn = get_connection()

    try:
        train(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
