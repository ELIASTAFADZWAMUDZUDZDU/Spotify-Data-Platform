# CV / Portfolio Description

## CV (short)
**Spotify Data Platform – End-to-End Data Engineering, Analytics and ML Project** | Python, PostgreSQL, SQL, pandas, scikit-learn, TensorFlow, Power BI, Streamlit
- Designed a normalised nine-table PostgreSQL schema and Python ETL scripts that load a 114,000-row public Spotify tracks dataset and generate a synthetic user and listening-history dataset (~1.08 million listening events).
- Built a SQL reporting layer of four views (one fact, three dimensions) and a four-page Power BI report (import mode, one-to-many relationships, DAX measures, Top N filters) covering platform KPIs, listening behaviour, users and the music catalogue.
- Developed a Streamlit app exposing a content-based track recommender (k-NN, cosine similarity), a RandomForest popularity predictor and a Keras genre classifier trained on PostgreSQL data.

## Portfolio paragraph
Spotify Data Platform is an end-to-end project that follows data from source to insight. A Python ETL pipeline normalises a public Spotify tracks dataset into a PostgreSQL schema and adds
a synthetic user and listening-history layer. PostgreSQL feeds two separate consumers: SQL reporting views that drive a four-page Power BI report, and a Python machine-learning layer
(a scikit-learn recommender, a popularity regressor and a Keras genre classifier) served through Streamlit. The project demonstrates database design, ETL, BI modelling,
machine learning and clear documentation. Listening and user data are simulated, so the analytics illustrate the platform's design rather than real listener behaviour.

## One-liner
End-to-end Spotify-style data platform: Python ETL → PostgreSQL → SQL views → Power BI, plus ML models in Streamlit.
