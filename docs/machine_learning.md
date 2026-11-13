# Machine Learning and Streamlit Application

All three models use the track catalogue read from PostgreSQL by `src/ml/feature_prep.py::load_tracks()` (tracks joined with album, artist and genre).

**Features:** four numeric audio features – `danceability`, `energy`, `valence`, `tempo` – plus `track_genre` where noted.

| Model | File | Library | Target / output | Method |
|---|---|---|---|---|
| Content-based recommender | `src/recommender/content_based.py` | scikit-learn | Top-N similar tracks with a similarity score | Standardise numeric features, one-hot encode genre, brute-force cosine `NearestNeighbors`; fitted at app start |
| Popularity predictor | `src/ml/popularity_model.py` | scikit-learn | Estimated popularity (0–100) | `Pipeline`: one-hot genre → `RandomForestRegressor` (150 trees, max depth 12, min leaf 5); 80/20 split; reports MAE and R² |
| Genre classifier | `src/ml/genre_classifier_tf.py` | **TensorFlow/Keras** | Genre + confidence over the 15 most frequent genres | Dense(32, ReLU) → Dropout(0.2) → Dense(16, ReLU) → softmax; scaler fitted on training data only; reports accuracy, top-3 accuracy and a confusion matrix |

The genre classifier is a Keras network, not a scikit-learn model (scikit-learn is used for its scaler, encoder and metrics).

## Training
```bash
python -m src.ml.popularity_model      # saves src/ml/artifacts/popularity_model.joblib
python -m src.ml.genre_classifier_tf   # saves genre_classifier.keras, genre_scaler.joblib, genre_label_encoder.joblib
```
Both print their evaluation metrics. **No metric values are quoted here because training could not be run without the database;** run the commands to obtain them.
The recommender needs no training step. It can be run from the command line: `python -m src.recommender.content_based --track "<name>" --n 5`.

## Streamlit app (`dashboard/app.py`)
```bash
streamlit run dashboard/app.py
```
Three pages selected from the sidebar: **Music Recommender** (pick a track, get 3–10 similar tracks with similarity %), **Genre Classifier**
(sliders for the four features → predicted genre and confidence) and **Popularity Predictor** (sliders plus a genre → estimated 0–100 score; labelled as a model estimate).
At start-up the app connects to PostgreSQL, loads the catalogue, fits the recommender and loads the saved Keras and joblib artifacts, so it requires the database, TensorFlow and the files in `src/ml/artifacts/`.

## Known limitations
- Audio features only: no lyrics, listening history or user data are used. Recommendations are item-to-item similarity, not personalised.
- The catalogue contains the same recording under several genres, so a "similar" track can be the same song with a different genre label.
- The popularity target is the dataset's snapshot popularity, and only four audio features plus genre are used, so predictions are coarse estimates.
- The saved joblib artifacts were pickled with scikit-learn 1.6.1 and may not load with other versions (see `requirements.txt`).
