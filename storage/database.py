import sqlite3

from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pdf_url TEXT NOT NULL UNIQUE,
    link_text TEXT,
    local_path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'descargado',
    error TEXT
);

CREATE TABLE IF NOT EXISTS fragments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page INTEGER,
    original_text TEXT NOT NULL,
    normalized_text TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_fragments_document ON fragments(document_id);
"""


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema():
    conn = connect()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()