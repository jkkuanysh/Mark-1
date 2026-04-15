"""
Configuration for PostgreSQL connection.
Edit the values below before running the project.
"""

def load_config():
    return {
        "host": "localhost",
        "dbname": "postgres",
        "user": "postgres",
        "password": "your_password_here",
        "port": 5432,
    }
