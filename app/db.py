import os
import sqlite3
from flask import g


def get_db(app):
    """Open a new DB connection if there is none in the current application context."""
    if "db" not in g:
        db_path = app.config["SQLITE_PATH"]
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Create the events table if it does not already exist."""
    db_path = app.config["SQLITE_PATH"]
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                event_id    TEXT PRIMARY KEY,
                type        TEXT NOT NULL,
                tenant_id   TEXT NOT NULL,
                severity    TEXT NOT NULL,
                message     TEXT NOT NULL,
                source      TEXT NOT NULL,
                metadata    TEXT,
                occurred_at TEXT,
                trace_id    TEXT,
                stored_at   TEXT NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()

    # Tear-down hook so each request closes its connection
    app.teardown_appcontext(close_db)
