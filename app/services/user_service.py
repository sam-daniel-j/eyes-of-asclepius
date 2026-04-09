import bcrypt
from app.database.connection import get_cursor, commit
from app.utils.id_generator import generate_user_public_id
from app.utils.crypto_keys import generate_rsa_keys


# =====================================================
# PASSWORD UTILITIES
# =====================================================

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


# =====================================================
# CREATE USER
# =====================================================

def create_user(username: str, password: str, role: str):

    role_map = {
        "doctor": "DOC",
        "patient": "PAT",
        "admin": "ADM"
    }

    role_prefix = role_map.get(role.lower())
    if not role_prefix:
        raise ValueError("Invalid role")

    cur = get_cursor()

    # Check duplicate username
    cur.execute(
        "SELECT id FROM users WHERE username = %s;",
        (username,)
    )
    if cur.fetchone():
        raise ValueError("Username already exists")

    public_id = generate_user_public_id(role_prefix)
    hashed_password = hash_password(password)

    rsa_public_key, rsa_private_key = generate_rsa_keys()

    cur.execute(
        """
        INSERT INTO users
        (public_id, username, password_hash, role, rsa_public_key, rsa_private_key)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, public_id, username, role;
        """,
        (
            public_id,
            username,
            hashed_password,
            role.lower(),
            rsa_public_key,
            rsa_private_key
        )
    )

    user = cur.fetchone()
    commit()

    if user:
        return dict(user)

    return None

    role_map = {
        "doctor": "DOC",
        "patient": "PAT",
        "admin": "ADM"
    }

    role_prefix = role_map.get(role.lower())
    if not role_prefix:
        raise ValueError("Invalid role")

    cur = get_cursor()

    # Check duplicate username
    cur.execute(
        "SELECT id FROM users WHERE username = %s;",
        (username,)
    )
    if cur.fetchone():
        raise ValueError("Username already exists")

    public_id = generate_user_public_id(role_prefix)
    hashed_password = hash_password(password)

    # 🔑 Generate RSA keys
    rsa_public_key, rsa_private_key = generate_rsa_keys()

    cur.execute(
        """
        INSERT INTO users
        (public_id, username, password_hash, role, rsa_public_key, rsa_private_key)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, public_id, username, role;
        """,
        (
            public_id,
            username,
            hashed_password,
            role.lower(),
            rsa_public_key,
            rsa_private_key
        )
    )

    user = cur.fetchone()
    commit()
    return user


# =====================================================
# AUTHENTICATE USER
# =====================================================

def authenticate_user(username: str, password: str):
    cur = get_cursor()

    cur.execute(
        "SELECT * FROM users WHERE username = %s;",
        (username,)
    )

    user = cur.fetchone()

    if not user:
        raise ValueError("Invalid username or password")

    if not verify_password(password, user["password_hash"]):
        raise ValueError("Invalid username or password")

    return user


# =====================================================
# FETCH USERS
# =====================================================

def get_user_by_id(user_id: int):
    cur = get_cursor()
    cur.execute("SELECT * FROM users WHERE id = %s;", (user_id,))
    return cur.fetchone()


def get_user_by_public_id(public_id: str):
    cur = get_cursor()
    cur.execute(
        "SELECT * FROM users WHERE public_id = %s;",
        (public_id,)
    )
    return cur.fetchone()


def get_user_by_username(username: str):
    cur = get_cursor()
    cur.execute("SELECT * FROM users WHERE username = %s;", (username,))
    return cur.fetchone()


def get_users_by_role(role: str):
    cur = get_cursor()
    cur.execute(
        "SELECT id, public_id, username FROM users WHERE role = %s ORDER BY id;",
        (role.lower(),)
    )
    return cur.fetchall()


# =====================================================
# DELETE USER (ADMIN FUNCTION)
# =====================================================

def delete_user(user_id: int):
    cur = get_cursor()
    cur.execute("DELETE FROM users WHERE id = %s;", (user_id,))
    commit()
