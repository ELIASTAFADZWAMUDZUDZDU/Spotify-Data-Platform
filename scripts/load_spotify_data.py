from pathlib import Path
import pandas as pd

from src.config.database import get_connection

# -------------------------
# Connect to PostgreSQL
# -------------------------

connection = get_connection()
cursor = connection.cursor()

print("Connected to PostgreSQL successfully!")

# -------------------------
# Read Dataset
# -------------------------

DATA_PATH = Path("data/raw/spotify_tracks.csv")

df = pd.read_csv(DATA_PATH)

print("Dataset loaded successfully!")



# -------------------------
# Load Genres
# -------------------------
# database/seed.sql only inserts 10 generic genres, none of which match the
# dataset's 114 lowercase genre names (e.g. "acoustic", "k-pop"). Insert the
# dataset's genres here so the track loader can resolve every genre_id.

dataset_genres = sorted(df["track_genre"].dropna().unique())

for genre in dataset_genres:
    cursor.execute(
        """
        INSERT INTO genre (genre_name)
        VALUES (%s)
        ON CONFLICT (genre_name) DO NOTHING;
        """,
        (genre,)
    )

connection.commit()

print(f"Genres loaded: {len(dataset_genres)}")

# -------------------------
# Extract Artists
# -------------------------

all_artists = []

for artists in df["artists"].dropna():

    artist_list = artists.split(";")

    for artist in artist_list:
        all_artists.append(artist.strip())

print(f"Total artist entries: {len(all_artists)}")

unique_artists = sorted(set(all_artists))

print(f"Unique artists: {len(unique_artists)}")

print("\nFirst 20 Artists:")

for artist in unique_artists[:20]:
    print(artist)

# -------------------------
# Load Artists
# -------------------------

for artist in unique_artists:
    cursor.execute(
        """
        INSERT INTO artist (artist_name)
        VALUES (%s)
        ON CONFLICT (artist_name) DO NOTHING;
        """,
        (artist,)
    )

connection.commit()

print("Artists loaded successfully!")  

# -------------------------
# Extract Albums
# -------------------------

albums = set()

for _, row in df.iterrows():

    # Skip rows with missing values
    if pd.isna(row["artists"]) or pd.isna(row["album_name"]):
        continue

    # Split artists
    artist_list = row["artists"].split(";")

    for artist in artist_list:

        artist = artist.strip()

        # Find artist_id
        cursor.execute(
            """
            SELECT artist_id
            FROM artist
            WHERE artist_name = %s;
            """,
            (artist,)
        )

        result = cursor.fetchone()

        if result:

            artist_id = result[0]

            albums.add(
                (
                    row["album_name"],
                    artist_id
                )
            )

print(f"Unique albums: {len(albums)}")

# -------------------------
# Load Albums
# -------------------------

for album_name, artist_id in albums:

    cursor.execute(
        """
        INSERT INTO album
        (
            album_name,
            artist_id
        )
        VALUES
        (
            %s,
            %s
        )
        ON CONFLICT (album_name, artist_id)
        DO NOTHING;
        """,
        (
            album_name,
            artist_id
        )
    )

connection.commit()

print("Albums loaded successfully!")

# -------------------------
# Build Artist Lookup
# -------------------------

artist_lookup = {}

cursor.execute(
    """
    SELECT
        artist_id,
        artist_name
    FROM artist;
    """
)

for artist_id, artist_name in cursor.fetchall():

    artist_lookup[artist_name] = artist_id

print(f"Artist lookup loaded: {len(artist_lookup)}")

# -------------------------
# Build Album Lookup
# -------------------------

album_lookup = {}

cursor.execute(
    """
    SELECT
        album_id,
        album_name,
        artist_id
    FROM album;
    """
)

for album_id, album_name, artist_id in cursor.fetchall():

    cursor.execute(
        """
        SELECT artist_name
        FROM artist
        WHERE artist_id = %s;
        """,
        (artist_id,)
    )

    artist_name = cursor.fetchone()[0]

    album_lookup[(artist_name, album_name)] = album_id

print(f"Album lookup loaded: {len(album_lookup)}")

# -------------------------
# Build Genre Lookup
# -------------------------

genre_lookup = {}

cursor.execute(
    """
    SELECT
        genre_id,
        genre_name
    FROM genre;
    """
)

for genre_id, genre_name in cursor.fetchall():

    genre_lookup[genre_name] = genre_id

print(f"Genre lookup loaded: {len(genre_lookup)}")

# -------------------------
# Load Tracks
# -------------------------

track_count = 0

for _, row in df.iterrows():

    if (
        pd.isna(row["artists"])
        or pd.isna(row["album_name"])
        or pd.isna(row["track_name"])
        or pd.isna(row["track_genre"])
    ):
        continue

    first_artist = row["artists"].split(";")[0].strip()

    artist_id = artist_lookup.get(first_artist)

    album_id = album_lookup.get(
        (
            first_artist,
            row["album_name"]
        )
    )

    genre_id = genre_lookup.get(
        row["track_genre"]
    )

    if artist_id is None:
        print("Missing artist:", first_artist)
        break

    if album_id is None:
        print("Missing album:", first_artist, "-", row["album_name"])
        break

    if genre_id is None:
        print("Missing genre:", row["track_genre"])
        break

    duration_seconds = int(row["duration_ms"] / 1000)

    tempo = row["tempo"]
    if pd.isna(tempo) or tempo <= 0:
        tempo = None

    cursor.execute(
        """
        INSERT INTO track
        (
            album_id,
            genre_id,
            track_name,
            duration_seconds,
            popularity,
            danceability,
            energy,
            valence,
            tempo
        )
        VALUES
        (
            %s,%s,%s,%s,%s,%s,%s,%s,%s
        );
        """,
        (
            album_id,
            genre_id,
            row["track_name"],
            duration_seconds,
            row["popularity"],
            row["danceability"],
            row["energy"],
            row["valence"],
            tempo
        )
    )

    track_count += 1

connection.commit()

print(f"Tracks loaded successfully: {track_count}")