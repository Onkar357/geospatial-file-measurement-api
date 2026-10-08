import sqlite3
from datetime import datetime, timezone

from app.config import DB_PATH


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS processing_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                feature_count INTEGER NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.commit()


def record_processing(filename, size_bytes, feature_count, status):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO processing_metadata "
            "(filename,size_bytes,feature_count,status,created_at) VALUES (?,?,?,?,?)",
            (filename, size_bytes, feature_count, status,
             datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
