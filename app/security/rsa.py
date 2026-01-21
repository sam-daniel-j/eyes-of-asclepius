import base64
from typing import cast
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import (
    load_pem_public_key,
    load_pem_private_key,
)

from app.config import Config


def generate_rsa_keypair():
    """
    Generates an RSA public/private key pair.

    Returns:
        (public_key_pem, private_key_pem) as UTF-8 strings
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=Config.RSA_KEY_SIZE,
        backend=default_backend()
    )

    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return (
        public_pem.decode("utf-8"),
        private_pem.decode("utf-8")
    )


def encrypt_with_public_key(data: bytes, public_key_pem: str) -> str:
    """
    Encrypts data using an RSA public key.

    Args:
        data: bytes to encrypt (typically AES key)
        public_key_pem: RSA public key in PEM format (string)

    Returns:
        Base64 encoded ciphertext (string)
    """
    public_key = cast(
        rsa.RSAPublicKey,
        load_pem_public_key(
            public_key_pem.encode("utf-8"),
            backend=default_backend()
        )
    )

    encrypted = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return base64.b64encode(encrypted).decode("utf-8")


def decrypt_with_private_key(ciphertext_b64: str, private_key_pem: str) -> bytes:
    """
    Decrypts RSA-encrypted Base64 ciphertext using a private key.

    Args:
        ciphertext_b64: Base64 encoded ciphertext
        private_key_pem: RSA private key in PEM format (string)

    Returns:
        Decrypted bytes
    """
    private_key = cast(
        rsa.RSAPrivateKey,
        load_pem_private_key(
            private_key_pem.encode("utf-8"),
            password=None,
            backend=default_backend()
        )
    )

    decrypted = private_key.decrypt(
        base64.b64decode(ciphertext_b64),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    return decrypted
