import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import Config


# Single shared connection (safe for Streamlit)
_connection = None


def get_connection():
    """
    Returns a PostgreSQL connection.
    Creates it if it doesn't exist or was closed.
    """
    global _connection

    if _connection is None or _connection.closed:
        _connection = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            cursor_factory=RealDictCursor
        )

    return _connection


def get_cursor():
    """
    Returns a cursor using RealDictCursor
    so results are dictionaries.
    """
    conn = get_connection()
    return conn.cursor()


def commit():
    """
    Commit the current transaction.
    """
    conn = get_connection()
    conn.commit()


def close_connection():
    """
    Close the database connection cleanly.
    """
    global _connection
    if _connection and not _connection.closed:
        _connection.close()
        _connection = None
