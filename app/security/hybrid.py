from typing import Dict

from app.security.aes import (
    generate_aes_key,
    encrypt_data,
    decrypt_data
)
from app.security.rsa import (
    encrypt_with_public_key,
    decrypt_with_private_key
)


def encrypt_medical_record(
    plain_text: str,
    recipient_public_keys: Dict[int, str]
) -> dict:
    """
    Encrypts a medical record using hybrid encryption.

    Args:
        plain_text: Medical record data (string)
        recipient_public_keys: dict {user_id: rsa_public_key_pem}

    Returns:
        {
            encrypted_data,
            iv,
            encrypted_keys: {user_id: encrypted_aes_key}
        }
    """
    if not plain_text:
        raise ValueError("Medical record data cannot be empty")

    # 1. Generate AES key
    aes_key = generate_aes_key()

    # 2. Encrypt medical data with AES
    encrypted_payload = encrypt_data(plain_text, aes_key)

    # 3. Encrypt AES key for each recipient
    encrypted_keys = {}
    for user_id, public_key_pem in recipient_public_keys.items():
        encrypted_keys[user_id] = encrypt_with_public_key(
            aes_key,
            public_key_pem
        )

    return {
        "encrypted_data": encrypted_payload["ciphertext"],
        "iv": encrypted_payload["iv"],
        "encrypted_keys": encrypted_keys
    }


def decrypt_medical_record(
    encrypted_data: str,
    iv: str,
    encrypted_aes_key: str,
    private_key_pem: str
) -> str:
    """
    Decrypts a medical record using hybrid encryption.

    Args:
        encrypted_data: Base64 AES ciphertext
        iv: Base64 IV
        encrypted_aes_key: AES key encrypted with RSA
        private_key_pem: User's RSA private key PEM

    Returns:
        Decrypted medical record (string)
    """
    # 1. Decrypt AES key using RSA private key
    aes_key = decrypt_with_private_key(
        encrypted_aes_key,
        private_key_pem
    )

    # 2. Decrypt medical data using AES key
    return decrypt_data(
        encrypted_data,
        iv,
        aes_key
    )
