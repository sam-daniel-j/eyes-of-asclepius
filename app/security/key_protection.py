import os
import base64
from typing import Tuple

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


PBKDF2_ITERATIONS = 100_000


def _derive_key(password: str, salt: bytes) -> bytes:
    """
    Derives a 256-bit key from a password using PBKDF2.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
        backend=default_backend()
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_private_key(private_key_pem: str, password: str) -> Tuple[str, str]:
    """
    Encrypts RSA private key using a password-derived key.

    Returns:
        (encrypted_private_key_b64, salt_b64)
    """
    salt = os.urandom(16)
    key = _derive_key(password, salt)

    iv = os.urandom(16)

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(private_key_pem.encode("utf-8")) + padder.finalize()

    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )

    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    encrypted_blob = iv + ciphertext

    return (
        base64.b64encode(encrypted_blob).decode("utf-8"),
        base64.b64encode(salt).decode("utf-8")
    )


def decrypt_private_key(
    encrypted_private_key_b64: str,
    salt_b64: str,
    password: str
) -> str:
    """
    Decrypts RSA private key using password.
    """
    encrypted_blob = base64.b64decode(encrypted_private_key_b64)
    salt = base64.b64decode(salt_b64)

    iv = encrypted_blob[:16]
    ciphertext = encrypted_blob[16:]

    key = _derive_key(password, salt)

    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )

    decryptor = cipher.decryptor()
    padded_key = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    private_key = unpadder.update(padded_key) + unpadder.finalize()

    return private_key.decode("utf-8")
