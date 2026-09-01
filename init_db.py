"""Initialize SQLite DB that holds movies and ratings separately."""

import pathlib
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

CREATE VIEW IF NOT EXISTS movie_ratings AS
SELECT
    m.id AS movie_id,
    m.title,
    m.year,
    m.director,
    m.genre,
    COUNT(r.id) AS ratings_count,
    ROUND(AVG(r.score), 2) AS avg_rating
FROM movies m
LEFT JOIN ratings r ON r.movie_id = m.id
GROUP BY m.id;

CREATE VIEW IF NOT EXISTS movie_ratings_detailed AS
SELECT
    r.id AS rating_id,
    m.id AS movie_id,
    m.title,
    m.year,
    m.director,
    m.genre,
    r.reviewer_id,
    rev.username AS reviewer,
    rev.display_name AS reviewer_display_name,
    r.score,
    r.comment,
    r.created_at
FROM ratings r
JOIN movies m ON m.id = r.movie_id
JOIN reviewers rev ON rev.id = r.reviewer_id
ORDER BY m.title, r.score DESC;
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
]

SEED_REVIEWERS = [
    ("alice", "Alice Johnson"),
    ("bob", "Bob Smith"),
    ("carol", "Carol Williams"),
    ("dave", "Dave Brown"),
    ("eve", "Eve Davis"),
    ("frank", "Frank Miller"),
]

SEED_RATINGS = [

    ("Sueños de libertad", 1, 9.5, "Perfect storytelling"),
    ("Sueños de libertad", 2, 9.3, "Uplifting and powerful"),
    ("Sueños de libertad", 3, 9.4, "Timeless classic"),
    ("Sueños de libertad", 4, 9.6, "Best movie ever"),
    ("Sueños de libertad", 5, 9.2, "Emotional"),

    ("El Padrino", 1, 9.4, "Masterpiece"),
    ("El Padrino", 2, 9.2, "Iconic performances"),
    ("El Padrino", 3, 9.3, "Brilliant directing"),
    ("El Padrino", 6, 9.0, "A bit long but great"),

    ("El Caballero Oscuro", 1, 9.0, "Heath Ledger unforgettable"),
    ("El Caballero Oscuro", 2, 9.2, "Best superhero film"),
    ("El Caballero Oscuro", 3, 8.9, "Amazing action"),
    ("El Caballero Oscuro", 4, 9.1, "Dark and gripping"),
    ("El Caballero Oscuro", 5, 8.8, "Great rewatch value"),

    ("Doce hombres sin piedad", 1, 9.0, "Tense dialogue"),
    ("Doce hombres sin piedad", 2, 8.9, "Brilliant courtroom drama"),
    ("Doce hombres sin piedad", 3, 9.1, "Perfect ensemble"),

    ("La lista de Schindler", 1, 9.0, "Heartbreaking"),
    ("La lista de Schindler", 2, 9.1, "Important film"),
    ("La lista de Schindler", 4, 8.9, "Powerful"),
    ("La lista de Schindler", 5, 9.2, "Must watch"),

    ("El Señor de los Anillos: El retorno del Rey", 1, 9.0, "Epic finale"),
    ("El Señor de los Anillos: El retorno del Rey", 2, 8.9, "Visually stunning"),
    ("El Señor de los Anillos: El retorno del Rey", 3, 9.1, "Emotional payoff"),
    ("El Señor de los Anillos: El retorno del Rey", 6, 8.8, "A bit long"),

    ("Tiempos violentos", 1, 8.9, "Quentin at his best"),
    ("Tiempos violentos", 2, 8.8, "Iconic dialogue"),
    ("Tiempos violentos", 3, 9.0, "Non-linear brilliance"),
    ("Tiempos violentos", 4, 8.7, "Cool and violent"),

    ("Forrest Gump", 1, 8.8, "Heartwarming"),
    ("Forrest Gump", 2, 8.9, "Tom Hanks amazing"),
    ("Forrest Gump", 5, 8.7, "Feel-good classic"),
    ("Forrest Gump", 6, 8.6, "A bit sentimental"),

    ("El club de la pelea", 1, 8.8, "Mind-bending"),
    ("El club de la pelea", 2, 8.7, "Great twist"),
    ("El club de la pelea", 3, 8.9, "Cult classic"),
    ("El club de la pelea", 4, 8.6, "Dark humor"),

    ("El origen", 1, 8.8, "Mind-bending sci-fi"),
    ("El origen", 2, 8.7, "Complex but rewarding"),
    ("El origen", 3, 8.9, "Nolan masterpiece"),
    ("El origen", 5, 8.6, "Great visuals"),
    ("El origen", 6, 8.5, "Confusing at times"),

    ("Matrix", 1, 8.7, "Revolutionary"),
    ("Matrix", 2, 8.8, "Groundbreaking effects"),
    ("Matrix", 3, 8.6, "Philosophical"),
    ("Matrix", 4, 8.5, "A bit dated"),

    ("Buenos muchachos", 1, 8.7, "Gritty crime classic"),
    ("Buenos muchachos", 2, 8.6, "Scorsese at his best"),
    ("Buenos muchachos", 3, 8.8, "Great narration"),

    ("Interestelar", 1, 8.7, "Emotional sci-fi"),
    ("Interestelar", 2, 8.6, "Visually epic"),
    ("Interestelar", 3, 8.8, "Hans Zimmer score"),
    ("Interestelar", 4, 8.5, "Science heavy"),
    ("Interestelar", 5, 8.9, "Loved the ending"),

    ("El viaje de Chihiro", 1, 8.6, "Magical"),
    ("El viaje de Chihiro", 2, 8.7, "Beautiful animation"),
    ("El viaje de Chihiro", 3, 8.5, "Whimsical"),
    ("El viaje de Chihiro", 5, 8.8, "Miyazaki genius"),

    ("Parásitos", 1, 8.5, "Clever twist"),
    ("Parásitos", 2, 8.6, "Social commentary"),
    ("Parásitos", 3, 8.7, "Brilliant"),
    ("Parásitos", 4, 8.4, "Dark comedy"),

    ("El silencio de los corderos", 1, 8.6, "Chilling"),
    ("El silencio de los corderos", 2, 8.5, "Hopkins iconic"),
    ("El silencio de los corderos", 3, 8.7, "Tense thriller"),

    ("Rescatando al soldado Ryan", 1, 8.6, "Brutal opening"),
    ("Rescatando al soldado Ryan", 2, 8.5, "Powerful war film"),
    ("Rescatando al soldado Ryan", 3, 8.7, "Realistic"),
    ("Rescatando al soldado Ryan", 4, 8.6, "Emotional"),

    ("Ciudad de Dios", 1, 8.6, "Raw and intense"),
    ("Ciudad de Dios", 2, 8.5, "Brazilian classic"),
    ("Ciudad de Dios", 3, 8.7, "Gritty"),

    ("Whiplash: Música y obsesión", 1, 8.5, "Intense drumming"),
    ("Whiplash: Música y obsesión", 2, 8.6, "J.K. Simmons amazing"),
    ("Whiplash: Música y obsesión", 3, 8.4, "Stressful but great"),
    ("Whiplash: Música y obsesión", 4, 8.7, "Perfect pace"),

    ("Amigos intocables", 1, 8.5, "Heartwarming"),
    ("Amigos intocables", 2, 8.4, "Funny and touching"),
    ("Amigos intocables", 3, 8.6, "Great chemistry"),
    ("Amigos intocables", 5, 8.5, "Feel-good"),

    ("El Padrino: Parte II", 1, 9.0, "Even better than first"),
    ("El Padrino: Parte II", 2, 8.9, "De Niro excellent"),
    ("El Padrino: Parte II", 3, 9.1, "Epic saga"),

    ("Milagros inesperados", 1, 8.6, "Emotional"),
    ("Milagros inesperados", 2, 8.5, "Touching"),
    ("Milagros inesperados", 3, 8.7, "Great adaptation"),
    ("Milagros inesperados", 4, 8.4, "A bit long"),

    ("Gladiador", 1, 8.5, "Epic battles"),
    ("Gladiador", 2, 8.6, "Crowe powerful"),
    ("Gladiador", 3, 8.4, "Great score"),
    ("Gladiador", 4, 8.7, "Classic"),

    ("Los infiltrados", 1, 8.5, "Tense undercover"),
    ("Los infiltrados", 2, 8.6, "Great cast"),
    ("Los infiltrados", 3, 8.4, "Twisty"),
    ("Los infiltrados", 5, 8.7, "Scorsese thriller"),

    ("El truco final", 1, 8.5, "Twisty magic"),
    ("El truco final", 2, 8.6, "Bale and Jackman great"),
    ("El truco final", 3, 8.7, "Nolan puzzle"),
    ("El truco final", 4, 8.4, "Rewatch reveals more"),
]


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
                for title, reviewer_id, score, comment in SEED_RATINGS:
                    cur = conn.execute("SELECT id FROM movies WHERE title = ?", (title,))
                    row = cur.fetchone()
                    if row is None:
                        continue
                    (movie_id,) = row
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
    conn = get_connection()
    try:
        movies = conn.execute("SELECT COUNT(*) AS c FROM movies").fetchone()["c"]
        ratings = conn.execute("SELECT COUNT(*) AS c FROM ratings").fetchone()["c"]
        print(f"movies={movies} ratings={ratings}")
        for row in conn.execute("SELECT title, year, avg_rating, ratings_count FROM movie_ratings ORDER BY avg_rating DESC LIMIT 5"):
            print(dict(row))
    finally:
        conn.close()
