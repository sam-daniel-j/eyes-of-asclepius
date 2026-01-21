from typing import Optional

from app.security.hashing import hash_password
from app.security.rsa import generate_rsa_keypair
from app.security.key_protection import encrypt_private_key
from app.models.user_model import (
    create_user,
    get_user_by_username
)


def register_user(
    username: str,
    password: str,
    role: str,
    specialization: Optional[str] = None
) -> int:
    """
    Registers a new user (admin / doctor / patient).

    Steps:
    1. Validate role
    2. Hash password (bcrypt)
    3. Generate RSA key pair
    4. Encrypt RSA private key using password (PBKDF2 + AES)
    5. Store user securely in database
    """

    # -------------------------
    # Validate role
    # -------------------------
    if role not in ("admin", "doctor", "patient"):
        raise ValueError("Invalid role")

    # Only doctors can have specialization
    if role != "doctor":
        specialization = None

    # -------------------------
    # Check for duplicate user
    # -------------------------
    if get_user_by_username(username):
        raise ValueError("Username already exists")

    # -------------------------
    # Hash password
    # -------------------------
    password_hash = hash_password(password)

    # -------------------------
    # Generate RSA keys
    # -------------------------
    public_key, private_key = generate_rsa_keypair()

    # -------------------------
    # Encrypt private key with password
    # -------------------------
    encrypted_private_key, private_key_salt = encrypt_private_key(
        private_key,
        password
    )

    # -------------------------
    # Store user in DB
    # -------------------------
    user_id = create_user(
        username=username,
        password_hash=password_hash,
        role=role,
        specialization=specialization,
        rsa_public_key=public_key,
        rsa_private_key_encrypted=encrypted_private_key,
        private_key_salt=private_key_salt
    )

    return user_id
