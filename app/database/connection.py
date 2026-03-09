import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import Config


# =====================================================
# DATABASE CONNECTION
# =====================================================

try:
    connection = psycopg2.connect(
        dbname=Config.DB_NAME,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        host=Config.DB_HOST,
        port=Config.DB_PORT,
    )

    connection.autocommit = False

except Exception as e:
    raise RuntimeError(f"Database connection failed: {e}")


# =====================================================
# CURSOR
# =====================================================

def get_cursor():
    """
    Returns rows as dictionaries instead of tuples.
    """
    return connection.cursor(cursor_factory=RealDictCursor)


# =====================================================
# COMMIT / ROLLBACK
# =====================================================

def commit():
    connection.commit()


def rollback():
    connection.rollback()


# =====================================================
# CLOSE CONNECTION (OPTIONAL)
# =====================================================

def close_connection():
    if connection:
        connection.close()