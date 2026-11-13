# Engineering Principles

Principles the project follows, with where each is visible in the code.

1. **PostgreSQL is the source of truth.** BI and ML both read from the database; nothing writes back. (`src/ml/feature_prep.py`, `database/powerbi_views.sql`)
2. **Model the data properly.** Normalised tables, primary/foreign keys and CHECK constraints (e.g. popularity 0–100, duration > 0) enforce integrity at the database level. (`database/schema.sql`)
3. **Views are the BI contract.** Power BI depends on four flat `bi_*` views, so the transactional schema can change without breaking the report. Business rules such as the skip threshold live in SQL once.
4. **Keep BI and ML separate.** Aggregate reporting goes through SQL and Power BI; row-level modelling goes through Python and Streamlit.
5. **Keep logic out of the UI.** Streamlit only collects inputs and displays results; features, training and prediction live in `src/`. (`dashboard/app.py` vs `src/ml`, `src/recommender`)
6. **Never commit secrets.** Connection settings come from `.env`, which is git-ignored; `.env.example` documents the variables. (`src/config/database.py`, `.gitignore`)
7. **Make runs repeatable.** Dataset-level inserts use `ON CONFLICT DO NOTHING` where possible, scripts run from the project root with `python -m`, and the run order is documented. Known exceptions (track and synthetic-data loaders are not idempotent) are documented in [ETL](etl_pipeline.md).
8. **Prevent leakage in ML.** Train/test split before fitting scalers; the scaler is fitted on training data only. (`src/ml/genre_classifier_tf.py`)
9. **Be honest in documentation.** Synthetic data, unverified components and open issues are stated explicitly.
10. **Test what can be tested without infrastructure.** Unit tests run on synthetic data and static SQL checks. (`tests/`)
