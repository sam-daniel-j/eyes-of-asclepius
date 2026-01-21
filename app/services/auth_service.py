from typing import Dict, Any

from app.models.user_model import get_user_by_username
from app.security.hashing import verify_password
from app.security.key_protection import decrypt_private_key


def authenticate_user(username: str, password: str) -> Dict[str, Any]:
    """
    Authenticates a user.

    Steps:
    1. Fetch user by username
    2. Verify password using bcrypt
    3. Decrypt RSA private key using password
    4. Return authenticated user data

    Raises:
        ValueError if authentication fails
    """

    # -------------------------
    # Fetch user
    # -------------------------
    user = get_user_by_username(username)
    if not user:
        raise ValueError("Invalid username or password")

    # -------------------------
    # Verify password
    # -------------------------
    if not verify_password(password, user["password_hash"]):
        raise ValueError("Invalid username or password")

    # -------------------------
    # Decrypt RSA private key
    # -------------------------
    try:
        private_key = decrypt_private_key(
            encrypted_private_key_b64=user["rsa_private_key_encrypted"],
            salt_b64=user["private_key_salt"],
            password=password
        )
    except Exception:
        # Covers wrong password, corrupted key, tampering
        raise ValueError("Invalid username or password")

    # -------------------------
    # Build authenticated user context
    # -------------------------
    return {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "specialization": user.get("specialization"),
        "rsa_public_key": user["rsa_public_key"],
        "rsa_private_key": private_key  # decrypted, kept in memory only
    }
