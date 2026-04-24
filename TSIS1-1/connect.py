"""
Database connection helper.
"""

import psycopg2
from config import load_config


def connect():
    """Create and return a PostgreSQL connection."""
    params = load_config()
    return psycopg2.connect(**params)
