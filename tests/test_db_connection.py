from app.database.connection import get_cursor

def test_db_connection():
    cur = get_cursor()
    cur.execute("SELECT 1;")
    assert cur.fetchone() is not None
