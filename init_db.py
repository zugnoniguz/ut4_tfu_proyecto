"""Initialize SQLite DB that holds movies and ratings separately."""

import pathlib
import random
import sqlite3

DB_PATH = pathlib.Path(__file__).parent / "app.db"

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    year INTEGER CHECK (year >= 1888),
    director TEXT,
    genre TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS reviewers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    display_name TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_id INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    reviewer_id INTEGER NOT NULL REFERENCES reviewers(id) ON DELETE CASCADE,
    score REAL NOT NULL CHECK (score >= 0 AND score <= 10),
    comment TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    UNIQUE(movie_id, reviewer_id)
);

CREATE INDEX IF NOT EXISTS idx_movies_title ON movies(title);
CREATE INDEX IF NOT EXISTS idx_reviewers_username ON reviewers(username);
CREATE INDEX IF NOT EXISTS idx_ratings_movie_id ON ratings(movie_id);
CREATE INDEX IF NOT EXISTS idx_ratings_reviewer_id ON ratings(reviewer_id);
CREATE INDEX IF NOT EXISTS idx_ratings_score ON ratings(score);
"""

SEED_MOVIES = [
    ("Sueños de libertad", 1994, "Frank Darabont", "Drama"),
    ("El Padrino", 1972, "Francis Ford Coppola", "Crimen"),
    ("El Caballero Oscuro", 2008, "Christopher Nolan", "Acción"),
    ("Doce hombres sin piedad", 1957, "Sidney Lumet", "Drama"),
    ("La lista de Schindler", 1993, "Steven Spielberg", "Biografía"),
    ("El Señor de los Anillos: El retorno del Rey", 2003, "Peter Jackson", "Aventura"),
    ("Tiempos violentos", 1994, "Quentin Tarantino", "Crimen"),
    ("Forrest Gump", 1994, "Robert Zemeckis", "Drama"),
    ("El club de la pelea", 1999, "David Fincher", "Drama"),
    ("El origen", 2010, "Christopher Nolan", "Ciencia ficción"),
    ("Matrix", 1999, "Lana Wachowski, Lilly Wachowski", "Ciencia ficción"),
    ("Buenos muchachos", 1990, "Martin Scorsese", "Crimen"),
    ("Interestelar", 2014, "Christopher Nolan", "Ciencia ficción"),
    ("El viaje de Chihiro", 2001, "Hayao Miyazaki", "Animación"),
    ("Parásitos", 2019, "Bong Joon-ho", "Suspenso"),
    ("El silencio de los corderos", 1991, "Jonathan Demme", "Suspenso"),
    ("Rescatando al soldado Ryan", 1998, "Steven Spielberg", "Bélico"),
    ("Ciudad de Dios", 2002, "Fernando Meirelles", "Crimen"),
    ("Whiplash: Música y obsesión", 2014, "Damien Chazelle", "Drama"),
    ("Amigos intocables", 2011, "Olivier Nakache & Éric Toledano", "Comedia"),
    ("El Padrino: Parte II", 1974, "Francis Ford Coppola", "Crimen"),
    ("Milagros inesperados", 1999, "Frank Darabont", "Drama"),
    ("Gladiador", 2000, "Ridley Scott", "Acción"),
    ("Los infiltrados", 2006, "Martin Scorsese", "Crimen"),
    ("El truco final", 2006, "Christopher Nolan", "Drama"),
    ("Titanic", 1997, "James Cameron", "Drama"),
    ("Avatar", 2009, "James Cameron", "Ciencia ficción"),
    ("Jurassic Park", 1993, "Steven Spielberg", "Aventura"),
    ("Toy Story", 1995, "John Lasseter", "Animación"),
    ("Coco", 2017, "Lee Unkrich", "Animación"),
    ("Avengers: Endgame", 2019, "Anthony Russo & Joe Russo", "Acción"),
    ("El Rey León", 1994, "Roger Allers & Rob Minkoff", "Animación"),
    ("Star Wars: Una nueva esperanza", 1977, "George Lucas", "Ciencia ficción"),
    ("Casablanca", 1942, "Michael Curtiz", "Drama"),
    ("Psicosis", 1960, "Alfred Hitchcock", "Suspenso"),
    ("El resplandor", 1980, "Stanley Kubrick", "Terror"),
    ("Volver al futuro", 1985, "Robert Zemeckis", "Ciencia ficción"),
    ("La La Land", 2016, "Damien Chazelle", "Musical"),
    ("Joker", 2019, "Todd Phillips", "Drama"),
    ("Dune: Parte uno", 2021, "Denis Villeneuve", "Ciencia ficción"),
]

SEED_REVIEWERS = [
    ("alice", "Alice Johnson"),
    ("bob", "Bob Smith"),
    ("carol", "Carol Williams"),
    ("dave", "Dave Brown"),
    ("eve", "Eve Davis"),
    ("frank", "Frank Miller"),
]

REVIEWER_RATING_COUNTS: dict[int, int] = {
    1: 38,  # alice
    2: 30,  # bob
    3: 23,  # carol
    4: 17,  # dave
    5: 11,  # eve
    6: 5,   # frank
}

SAMPLE_COMMENTS = [
    "Excelente",
    "Muy buena",
    "Obra maestra",
    "Me encantó",
    "Recomendada",
    "Inolvidable",
    "Buena pero larga",
    "Gran actuación",
    "Emotiva",
    "Visualmente impactante",
    "Un clásico",
    "Para ver de nuevo",
    "Intensa",
    "Divertida",
    "Conmovedora",
]


def _generate_ratings(movie_ids: list[int]) -> list[tuple[int, int, float, str]]:
    """Generate (movie_id, reviewer_id, score, comment) with distinct counts per reviewer."""
    rng = random.Random(42)
    ratings: list[tuple[int, int, float, str]] = []
    for reviewer_id, target_count in REVIEWER_RATING_COUNTS.items():
        chosen = rng.sample(movie_ids, target_count)
        for movie_id in chosen:
            score = round(rng.uniform(5.0, 10.0), 1)
            if score < 5.0:
                score = 5.0
            if score > 10.0:
                score = 10.0
            comment = rng.choice(SAMPLE_COMMENTS)
            ratings.append((movie_id, reviewer_id, score, comment))
    rng.shuffle(ratings)
    return ratings


def init_db(seed: bool = True) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)

        if seed:
            cur = conn.execute("SELECT COUNT(*) FROM movies")
            (count,) = cur.fetchone()
            if count == 0:
                for title, year, director, genre in SEED_MOVIES:
                    conn.execute(
                        "INSERT OR IGNORE INTO movies (title, year, director, genre) VALUES (?, ?, ?, ?)",
                        (title, year, director, genre),
                    )
                for idx, (username, display_name) in enumerate(SEED_REVIEWERS, start=1):
                    conn.execute(
                        "INSERT OR IGNORE INTO reviewers (id, username, display_name) VALUES (?, ?, ?)",
                        (idx, username, display_name),
                    )
                rows = conn.execute("SELECT id FROM movies").fetchall()
                movie_ids = [r[0] for r in rows]
                for movie_id, reviewer_id, score, comment in _generate_ratings(movie_ids):
                    conn.execute(
                        "INSERT OR IGNORE INTO ratings (movie_id, reviewer_id, score, comment) VALUES (?, ?, ?, ?)",
                        (movie_id, reviewer_id, score, comment),
                    )

        conn.commit()
    finally:
        conn.close()


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")
