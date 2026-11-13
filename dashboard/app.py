
"""
Spotify Data Platform
Streamlit Machine Learning Application

This application provides:
1. Content-based music recommendations
2. Music genre classification
3. Track popularity prediction

PostgreSQL is the source of truth.
Machine-learning logic remains inside src/.
Streamlit provides the user interface.
"""

import sys
from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


# --------------------------------------------------
# 1. PROJECT PATH
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# --------------------------------------------------
# 2. PROJECT IMPORTS
# --------------------------------------------------

from src.config.database import get_connection

from src.ml.feature_prep import load_tracks

from src.recommender.content_based import (
    prepare_features,
    train_recommender,
    recommend_songs,
)

from src.ml.genre_classifier_tf import predict_genre

from src.ml.popularity_model import predict_popularity


# --------------------------------------------------
# 3. STREAMLIT CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Spotify ML Application",
    page_icon="🎵",
    layout="wide",
)

st.title("Spotify Data Platform")

st.caption("Machine Learning Application")

st.markdown(
    """
    Explore music recommendations, classify music genres,
    and estimate track popularity using machine-learning models.
    """
)


# --------------------------------------------------
# 4. LOAD TRACK DATA AND RECOMMENDER
# --------------------------------------------------

@st.cache_resource
def load_recommender_resources():

    conn = get_connection()

    try:
        raw_tracks = load_tracks(conn)

    finally:
        conn.close()

    # Clean the tracks and transform their features.
    tracks, features = prepare_features(raw_tracks)

    # Fit KNN using the prepared features.
    recommender_model = train_recommender(features)

    return tracks, features, recommender_model


# --------------------------------------------------
# 5. LOAD GENRE CLASSIFIER
# --------------------------------------------------

@st.cache_resource
def load_genre_resources():

    import tensorflow as tf

    artifact_dir = (
        PROJECT_ROOT
        / "src"
        / "ml"
        / "artifacts"
    )

    model = tf.keras.models.load_model(
        artifact_dir / "genre_classifier.keras"
    )

    scaler = joblib.load(
        artifact_dir / "genre_scaler.joblib"
    )

    label_encoder = joblib.load(
        artifact_dir / "genre_label_encoder.joblib"
    )

    return model, scaler, label_encoder


# --------------------------------------------------
# 6. LOAD POPULARITY MODEL
# --------------------------------------------------

@st.cache_resource
def load_popularity_resources():

    artifact_path = (
        PROJECT_ROOT
        / "src"
        / "ml"
        / "artifacts"
        / "popularity_model.joblib"
    )

    return joblib.load(artifact_path)


# --------------------------------------------------
# 7. INITIALISE APPLICATION RESOURCES
# --------------------------------------------------

try:

    tracks, recommender_features, recommender_model = (
        load_recommender_resources()
    )

    genre_model, genre_scaler, genre_encoder = (
        load_genre_resources()
    )

    popularity_model = load_popularity_resources()

    st.success(
        f"Application ready — {len(tracks):,} tracks loaded."
    )

except Exception as error:

    st.error(
        f"Could not initialise the application: {error}"
    )

    st.stop()


# --------------------------------------------------
# 8. SIDEBAR NAVIGATION
# --------------------------------------------------

page = st.sidebar.radio(
    "Machine Learning Tools",
    [
        "Music Recommender",
        "Genre Classifier",
        "Popularity Predictor",
    ],
)


# --------------------------------------------------
# 9. MUSIC RECOMMENDER
# --------------------------------------------------

if page == "Music Recommender":

    st.header("Content-Based Music Recommender")

    st.write(
        "Select a track to discover other tracks with similar "
        "audio characteristics and genre information."
    )

    # Create a separate display DataFrame.
    display_tracks = tracks.copy()

    display_tracks["display_name"] = (
        display_tracks["track_name"].fillna("Unknown")
        + " — "
        + display_tracks["artist_name"].fillna("Unknown Artist")
    )

    selected_track = st.selectbox(
        "Choose a track",
        display_tracks["display_name"].tolist(),
    )

    number_of_recommendations = st.slider(
        "Number of recommendations",
        min_value=3,
        max_value=10,
        value=5,
    )

    if st.button("Find Similar Tracks"):

        selected_row = display_tracks[
            display_tracks["display_name"] == selected_track
        ].iloc[0]

        with st.spinner("Finding similar tracks..."):

            recommendations = recommend_songs(
                selected_row["track_name"],
                tracks,
                recommender_features,
                recommender_model,
                number_of_recommendations,
                track_id=selected_row["track_id"],
            )

        st.subheader("Recommended Tracks")

        if recommendations.empty:

            st.info("No recommendations were found.")

        else:

            recommendations["similarity"] = (
                recommendations["similarity"] * 100
            ).round(2)

            recommendations = recommendations.rename(
                columns={
                    "track_name": "Track",
                    "artist_name": "Artist",
                    "track_genre": "Genre",
                    "similarity": "Similarity (%)",
                }
            )

            st.dataframe(
                recommendations,
                use_container_width=True,
                hide_index=True,
            )


# --------------------------------------------------
# 10. GENRE CLASSIFIER
# --------------------------------------------------

elif page == "Genre Classifier":

    st.header("Music Genre Classification")

    st.write(
        "Enter a track's audio characteristics to predict "
        "its most likely genre."
    )

    col1, col2 = st.columns(2)

    with col1:

        danceability = st.slider(
            "Danceability",
            0.0, 1.0, 0.5, 0.01,
        )

        energy = st.slider(
            "Energy",
            0.0, 1.0, 0.5, 0.01,
        )

    with col2:

        valence = st.slider(
            "Valence",
            0.0, 1.0, 0.5, 0.01,
        )

        tempo = st.slider(
            "Tempo (BPM)",
            40.0, 220.0, 120.0, 1.0,
        )

    if st.button("Predict Genre"):

        audio_features = [
            danceability,
            energy,
            valence,
            tempo,
        ]

        with st.spinner("Classifying track..."):

            result = predict_genre(
                genre_model,
                genre_scaler,
                genre_encoder,
                audio_features,
            )

        st.subheader("Classification Result")

        col1, col2 = st.columns(2)

        col1.metric(
            "Predicted Genre",
            result["genre"],
        )

        col2.metric(
            "Model Confidence",
            f"{result['confidence']:.1%}",
        )


# --------------------------------------------------
# 11. POPULARITY PREDICTOR
# --------------------------------------------------

elif page == "Popularity Predictor":

    st.header("Track Popularity Prediction")

    st.write(
        "Estimate a track's popularity based on its audio "
        "characteristics and genre."
    )

    col1, col2 = st.columns(2)

    with col1:

        danceability = st.slider(
            "Danceability",
            0.0, 1.0, 0.5, 0.01,
            key="pop_danceability",
        )

        energy = st.slider(
            "Energy",
            0.0, 1.0, 0.5, 0.01,
            key="pop_energy",
        )

    with col2:

        valence = st.slider(
            "Valence",
            0.0, 1.0, 0.5, 0.01,
            key="pop_valence",
        )

        tempo = st.slider(
            "Tempo (BPM)",
            40.0, 220.0, 120.0, 1.0,
            key="pop_tempo",
        )

    available_genres = sorted(
        tracks["track_genre"].dropna().unique().tolist()
    )

    genre = st.selectbox(
        "Track Genre",
        available_genres,
    )

    if st.button("Predict Popularity"):

        with st.spinner("Estimating popularity..."):

            prediction = predict_popularity(
                popularity_model,
                danceability,
                energy,
                valence,
                tempo,
                genre,
            )

        st.subheader("Prediction Result")

        st.metric(
            "Estimated Popularity",
            f"{float(prediction):.1f} / 100",
        )

        st.caption(
            "This is a model estimate based on the selected "
            "audio features and genre, not an actual Spotify "
            "streaming or popularity measurement."
        )


# --------------------------------------------------
# 12. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Spotify Data Platform | Data Engineering, "
    "Business Intelligence and Machine Learning"
)
