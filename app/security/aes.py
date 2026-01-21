import os
import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
from app.config import Config


def generate_aes_key() -> bytes:
    """
    Generates a random AES-256 key.
    """
    return os.urandom(Config.AES_KEY_SIZE)  # 32 bytes = 256-bit


def encrypt_data(plain_text: str, aes_key: bytes) -> dict:
    """
    Encrypts plaintext using AES-256-CBC.

    Args:
        plain_text: Data to encrypt (string)
        aes_key: AES key (bytes)

    Returns:
        dict with base64 encoded ciphertext and iv
    """
    if not plain_text:
        raise ValueError("Data to encrypt cannot be empty")

    iv = os.urandom(16)  # AES block size = 16 bytes

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain_text.encode("utf-8")) + padder.finalize()

    cipher = Cipher(
        algorithms.AES(aes_key),
        modes.CBC(iv),
        backend=default_backend()
    )

    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    return {
        "ciphertext": base64.b64encode(ciphertext).decode("utf-8"),
        "iv": base64.b64encode(iv).decode("utf-8")
    }


def decrypt_data(ciphertext_b64: str, iv_b64: str, aes_key: bytes) -> str:
    """
    Decrypts AES-256-CBC encrypted data.

    Args:
        ciphertext_b64: Base64 ciphertext
        iv_b64: Base64 IV
        aes_key: AES key (bytes)

    Returns:
        Decrypted plaintext (string)
    """
    ciphertext = base64.b64decode(ciphertext_b64)
    iv = base64.b64decode(iv_b64)

    cipher = Cipher(
        algorithms.AES(aes_key),
        modes.CBC(iv),
        backend=default_backend()
    )

    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    plain_text = unpadder.update(padded_plaintext) + unpadder.finalize()

    return plain_text.decode("utf-8")
