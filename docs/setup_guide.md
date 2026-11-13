# Setup and Execution Guide

Run all commands from the project root. The database-dependent steps (loading, training, Streamlit) were written from reading the code and should be run once on your own machine.

## Prerequisites
- Python 3.10+ (TensorFlow must support your Python version)
- PostgreSQL 13+ with `psql` available
- Power BI Desktop (Windows) only to open the `.pbix`

## 1. Python environment
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configuration
```bash
cp .env.example .env               # then edit with your own credentials
```
Variables read by `src/config/database.py`: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`. Never commit `.env`.

## 3. Database and data
```bash
createdb spotify_platform
psql -d spotify_platform -f database/schema.sql
psql -d spotify_platform -f database/seed.sql
python -m scripts.load_spotify_data
python -m scripts.generate_and_load_transaction_data
psql -d spotify_platform -f database/indexes.sql
psql -d spotify_platform -f database/powerbi_views.sql
```
Both loaders are slow (row-by-row inserts); expect a long run. Run each loader **once** on an empty database (see [ETL notes](etl_pipeline.md)).
Quick check: `psql -d spotify_platform -c "SELECT COUNT(*) FROM bi_fact_listening;"`

## 4. Business intelligence
Open `powerbi/spotify_analytics.pbix` in Power BI Desktop. The report is in import mode, so it opens with its stored data;
refreshing from PostgreSQL currently fails with a cyclic-reference error (see [POWER_BI_DOCUMENTATION.md](POWER_BI_DOCUMENTATION.md#8-limitations)).

## 5. Machine learning and Streamlit
```bash
python -m src.ml.popularity_model          # optional: retrain
python -m src.ml.genre_classifier_tf       # optional: retrain
python -m src.recommender.content_based --track "Blinding Lights" --n 5
streamlit run dashboard/app.py
```

## 6. Tests
```bash
python -m unittest discover -s tests -t . -v
```
Nine tests cover the SQL files (static checks), the popularity pipeline and the recommender using synthetic data. No database is required;
the recommender tests need `psycopg2` installed (they are skipped otherwise).

## Troubleshooting
| Symptom | Cause / fix |
|---|---|
| `Missing genre: ...` from the catalogue loader | Use the updated loader, which inserts the dataset's genres first |
| `could not unpickle` / `_RemainderColsList` when loading the model | scikit-learn version differs from 1.6.1; install the pinned version or retrain |
| Streamlit shows "Could not initialise the application" | Database unreachable, empty `track` table, TensorFlow missing or artifacts missing |
