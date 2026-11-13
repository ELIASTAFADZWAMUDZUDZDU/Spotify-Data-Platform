# Business Requirements

> These requirements are **retrospective**: they describe what the implemented platform is meant to support, derived from the code, schema and reports in this repository.
> The platform is a portfolio project on simulated listening data, not a production system with real stakeholders.

## 1. Purpose
Provide a single, trustworthy data platform from which a music-streaming business can (a) report on listening, users and catalogue, and (b) offer simple data-driven music features.

## 2. Intended users
| User | Need |
|---|---|
| Business / product analyst | Dashboards on platform activity, listening behaviour, users and catalogue (Power BI) |
| Data analyst / engineer | A clean, documented, queryable database and repeatable load process (PostgreSQL, scripts) |
| Product / data-science audience | Interactive music recommendations, genre classification and popularity estimates (Streamlit) |

## 3. Business questions
| Area | Question | Delivered by |
|---|---|---|
| Platform | How many plays, users, tracks and active listeners are there, and how does daily activity change? | Power BI: Platform Overview |
| Platform | Which artists attract the most listening? How are users split by plan? | Power BI: Platform Overview |
| Listening | How many hours are listened to, how complete are listens, how many are likely skips? | Power BI: Listening Behaviour |
| Listening | Which genres and plans drive listening? | Power BI: Listening Behaviour |
| Users | Where are users, and how do signups grow over time and by country? | Power BI: User Analytics |
| Catalogue | Which tracks and genres are most popular; what is each genre's audio profile? | Power BI: Music Catalogue |
| Product | Which tracks are similar to a chosen track? What genre does an audio profile suggest? How popular might a track be? | Streamlit app |

## 4. Functional requirements
| ID | Requirement | Implemented in |
|---|---|---|
| FR1 | Store catalogue, users, playlists and listening events in a normalised relational database with integrity constraints | `database/schema.sql` |
| FR2 | Load a public track dataset into that schema | `scripts/load_spotify_data.py` |
| FR3 | Generate realistic-shaped users, playlists and listening history | `scripts/generate_and_load_transaction_data.py` |
| FR4 | Expose analysis-ready reporting views for BI | `database/powerbi_views.sql` |
| FR5 | Provide an interactive four-page dashboard | `powerbi/spotify_analytics.pbix` |
| FR6 | Recommend similar tracks from audio features and genre | `src/recommender/content_based.py` |
| FR7 | Predict track popularity and classify genre from audio features | `src/ml/` |
| FR8 | Provide a user interface for the ML features | `dashboard/app.py` |

## 5. Non-functional requirements
- **Single source of truth:** PostgreSQL; BI and ML read from it.
- **Separation of concerns:** BI (views → Power BI) is independent of ML (Python → Streamlit).
- **Reproducibility:** documented, ordered setup ([setup guide](setup_guide.md)).
- **Security:** credentials come from environment variables, never from source control.
- **Honesty about data:** simulated data is labelled as such throughout.

## 6. Out of scope / not implemented
Real user data, real-time or streaming ingestion, automated scheduling, personalised (user-based) recommendation, data refresh automation for Power BI, and deployment of the Streamlit app.
