"""
Database helper functions for TSIS3 Snake.
"""

import psycopg2
from config import load_config


def connect():
    """Create and return a PostgreSQL connection."""
    return psycopg2.connect(**load_config())


def setup_database():
    """Create required tables if they do not exist."""
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS game_sessions (
                    id SERIAL PRIMARY KEY,
                    player_id INTEGER REFERENCES players(id),
                    score INTEGER NOT NULL,
                    level_reached INTEGER NOT NULL,
                    played_at TIMESTAMP DEFAULT NOW()
                );
                """
            )
        conn.commit()


def get_or_create_player(username: str) -> int:
    """Return player id, creating the player if needed."""
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM players WHERE username = %s", (username,))
            row = cur.fetchone()
            if row:
                return row[0]

            cur.execute(
                "INSERT INTO players(username) VALUES (%s) RETURNING id",
                (username,),
            )
            player_id = cur.fetchone()[0]
        conn.commit()
    return player_id


def save_result(username: str, score: int, level_reached: int):
    """Save one finished game session."""
    player_id = get_or_create_player(username)
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO game_sessions(player_id, score, level_reached)
                VALUES (%s, %s, %s)
                """,
                (player_id, score, level_reached),
            )
        conn.commit()


def get_top_scores(limit: int = 10):
    """Return top scores with username, level, and date."""
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT p.username, g.score, g.level_reached, g.played_at
                FROM game_sessions g
                JOIN players p ON p.id = g.player_id
                ORDER BY g.score DESC, g.level_reached DESC, g.played_at ASC
                LIMIT %s
                """,
                (limit,),
            )
            return cur.fetchall()


def get_personal_best(username: str) -> int:
    """Return best score for the given username."""
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(MAX(g.score), 0)
                FROM game_sessions g
                JOIN players p ON p.id = g.player_id
                WHERE p.username = %s
                """,
                (username,),
            )
            return cur.fetchone()[0]
