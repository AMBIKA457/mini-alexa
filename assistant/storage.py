"""Tiny SQLite layer for notes. Uses parameterized queries (no SQL injection)."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from . import config


@contextmanager
def _conn():
    """Yield a configured SQLite connection and always close it."""
    con = sqlite3.connect(config.DB_PATH, timeout=5)
    try:
        con.execute("PRAGMA busy_timeout = 5000")
        con.execute(
            "CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, text TEXT NOT NULL, created TEXT NOT NULL)"
        )
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def add_note(text: str) -> None:
    with _conn() as con:
        con.execute("INSERT INTO notes (text, created) VALUES (?, ?)",
                    (text[:500], datetime.now().isoformat(timespec="seconds")))


def list_notes(limit: int = 5) -> list[str]:
    with _conn() as con:
        rows = con.execute("SELECT text FROM notes ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [r[0] for r in rows]


def clear_notes() -> None:
    with _conn() as con:
        con.execute("DELETE FROM notes")
