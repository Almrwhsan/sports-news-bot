import sqlite3

DB_NAME = "sports_news.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_database():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            source TEXT,
            published_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            posted INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()
    print("Database initialized successfully!")
