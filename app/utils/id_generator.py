from datetime import datetime
from app.database.connection import get_cursor, commit


def generate_user_public_id(role: str) -> str:
    role = role.upper()
    year = datetime.now().year
    cur = get_cursor()

    cur.execute(
        """
        INSERT INTO user_id_counters (role, year, last_value)
        VALUES (%s, %s, 1)
        ON CONFLICT (role, year)
        DO UPDATE
        SET last_value = user_id_counters.last_value + 1
        RETURNING last_value;
        """,
        (role, year)
    )

    result = cur.fetchone()

    if result is None:
        raise RuntimeError("Failed to generate public ID")

    commit()

    next_value = result["last_value"]
    return f"{role}-{year}-{next_value:04d}"