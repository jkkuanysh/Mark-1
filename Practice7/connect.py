"""Connection helpers for the PhoneBook project."""

from contextlib import contextmanager
import psycopg2
from config import DB_CONFIG


def get_connection():
    """Create and return a new PostgreSQL connection."""
    return psycopg2.connect(**DB_CONFIG)


@contextmanager
def db_cursor(commit: bool = False):
    """Context manager that yields a cursor and handles commit/rollback.

    Args:
        commit: If True, commit the transaction when the block succeeds.
    """
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        yield cur
        if commit:
            conn.commit()
    except Exception:
        if conn is not None:
            conn.rollback()
        raise
    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()
