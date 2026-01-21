from typing import Optional, Dict, Any, cast

from app.database.connection import get_cursor, commit


def create_user(
    username: str,
    password_hash: str,
    role: str,
    rsa_public_key: str,
    rsa_private_key_encrypted: str,
    private_key_salt: str,
    specialization: Optional[str] = None
) -> int:
    """
    Creates a new user and returns the user ID.
    """
    cur = get_cursor()

    cur.execute(
        """
        INSERT INTO users (
            username,
            password_hash,
            role,
            specialization,
            rsa_public_key,
            rsa_private_key_encrypted,
            private_key_salt
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """,
        (
            username,
            password_hash,
            role,
            specialization,
            rsa_public_key,
            rsa_private_key_encrypted,
            private_key_salt
        )
    )

    row = cast(Dict[str, Any], cur.fetchone())
    commit()

    return row["id"]


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """
    Fetches a user by username.
    """
    cur = get_cursor()
    cur.execute(
        "SELECT * FROM users WHERE username = %s;",
        (username,)
    )

    row = cur.fetchone()
    if row is None:
        return None

    return cast(Dict[str, Any], row)


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Fetches a user by ID.
    """
    cur = get_cursor()
    cur.execute(
        "SELECT * FROM users WHERE id = %s;",
        (user_id,)
    )

    row = cur.fetchone()
    if row is None:
        return None

    return cast(Dict[str, Any], row)
