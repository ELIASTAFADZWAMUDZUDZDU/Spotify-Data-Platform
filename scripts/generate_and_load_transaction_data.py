from datetime import date
import random

from faker import Faker

from src.config.database import get_connection

# -------------------------
# Faker
# -------------------------

fake = Faker()

# -------------------------
# PostgreSQL Connection
# -------------------------

connection = get_connection()
cursor = connection.cursor()

print("Connected to PostgreSQL successfully!")

# -------------------------
# Configuration
# -------------------------

NUM_USERS = 10000

# -------------------------
# Generate Users
# -------------------------

user_count = 0

for _ in range(NUM_USERS):

    username = fake.user_name()

    country = fake.country()

    signup_date = fake.date_between(
        start_date="-5y",
        end_date=date.today()
    )

    # 80% Free, 20% Premium
    plan_id = random.choices(
        population=[1, 2],
        weights=[80, 20],
        k=1
    )[0]

    cursor.execute(
        """
        INSERT INTO app_user
        (
            username,
            country,
            signup_date,
            plan_id
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s
        )
        ON CONFLICT (username) DO NOTHING;
        """,
        (
            username,
            country,
            signup_date,
            plan_id
        )
    )

    user_count += cursor.rowcount

# -------------------------
# Commit Changes
# -------------------------

connection.commit()

print(f"Users inserted successfully: {user_count}")

# -------------------------
# Close Connection
# -------------------------






# -------------------------
# Load Users
# -------------------------

cursor.execute(
    """
    SELECT user_id
    FROM app_user;
    """
)

users = cursor.fetchall()

print(f"Users loaded: {len(users)}")

# -------------------------
# Playlist Names
# -------------------------

playlist_names = [
    "Workout Mix",
    "Chill Vibes",
    "Road Trip",
    "Morning Coffee",
    "Coding Music",
    "Study Session",
    "Party Hits",
    "Late Night",
    "Focus Mode",
    "Favorites",
    "Top Songs",
    "Weekend Mix",
    "Relax",
    "Summer Hits",
    "Throwbacks",
    "Gym Hits",
    "Daily Mix",
    "Sleep",
    "Jazz Evening",
    "Happy Mood"
]

# -------------------------
# Generate Playlists
# -------------------------

playlist_count = 0

for (user_id,) in users:

    # 70% chance the user creates playlists
    if random.random() > 0.70:
        continue

    # Between 1 and 5 playlists
    number_of_playlists = random.randint(1, 5)

    for _ in range(number_of_playlists):

        playlist_name = random.choice(playlist_names)

        cursor.execute(
            """
            INSERT INTO playlist
            (
                user_id,
                playlist_name
            )
            VALUES
            (
                %s,
                %s
            );
            """,
            (
                user_id,
                playlist_name
            )
        )

        playlist_count += 1

connection.commit()

print(f"Playlists inserted successfully: {playlist_count}")

# -------------------------
# Load Playlists
# -------------------------

cursor.execute(
    """
    SELECT playlist_id
    FROM playlist;
    """
)

playlists = cursor.fetchall()

print(f"Playlists loaded: {len(playlists)}")

# -------------------------
# Load Tracks
# -------------------------

cursor.execute(
    """
    SELECT track_id
    FROM track;
    """
)

tracks = cursor.fetchall()

print(f"Tracks loaded: {len(tracks)}")

# -------------------------
# Generate Playlist Tracks
# -------------------------

playlist_track_count = 0

track_ids = [track_id for (track_id,) in tracks]

for (playlist_id,) in playlists:

    number_of_tracks = random.randint(20, 100)

    selected_tracks = random.sample(
        track_ids,
        number_of_tracks
    )

    for track_id in selected_tracks:

        cursor.execute(
            """
            INSERT INTO playlist_track
            (
                playlist_id,
                track_id
            )
            VALUES
            (
                %s,
                %s
            )
            ON CONFLICT DO NOTHING;
            """,
            (
                playlist_id,
                track_id
            )
        )

        playlist_track_count += cursor.rowcount

connection.commit()

print(f"Playlist Tracks inserted: {playlist_track_count}")

# -------------------------
# Load Users
# -------------------------

cursor.execute(
    """
    SELECT user_id
    FROM app_user;
    """
)

users = cursor.fetchall()

print(f"Users loaded: {len(users)}")

# -------------------------
# Load Tracks
# -------------------------

cursor.execute(
    """
    SELECT
        track_id,
        duration_seconds
    FROM track;
    """
)

tracks = cursor.fetchall()

print(f"Tracks loaded: {len(tracks)}")

# -------------------------
# Generate Listening History
# -------------------------

history_count = 0

for (user_id,) in users:

    number_of_listens = random.randint(20, 100)

    for _ in range(number_of_listens):

        track_id, duration_seconds = random.choice(tracks)

        listened_at = fake.date_time_between(
            start_date="-2y",
            end_date="now"
        )

        listening_duration = random.randint(
            max(1, int(duration_seconds * 0.30)),
            duration_seconds
        )

        cursor.execute(
            """
            INSERT INTO listening_history
            (
                user_id,
                track_id,
                listened_at,
                listening_duration
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s
            );
            """,
            (
                user_id,
                track_id,
                listened_at,
                listening_duration
            )
        )

        history_count += 1

connection.commit()

print(f"Listening History inserted: {history_count}")

# -------------------------
# Close Connection
# -------------------------

cursor.close()
connection.close()

print("Database connection closed.")