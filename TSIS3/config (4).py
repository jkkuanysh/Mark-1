"""
Database configuration for PostgreSQL.
Edit these values before running the game.
"""

def load_config():
    return {
        "host": "localhost",
        "dbname": "postgres",
        "user": "postgres",
        "password": "your_password_here",
        "port": 5432,
    }
