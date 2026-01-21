import os
from dotenv import load_dotenv

# Load variables from .env into environment
load_dotenv()


class Config:
    """
    Central configuration for Eyes of Asclepius.
    All environment-specific values are loaded from .env
    """

    # --------------------
    # Application
    # --------------------
    APP_NAME = os.getenv("APP_NAME", "Eyes of Asclepius")
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # --------------------
    # Database (PostgreSQL)
    # --------------------
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT", 5432))
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # --------------------
    # Security
    # --------------------
    BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", 12))
    RSA_KEY_SIZE = int(os.getenv("RSA_KEY_SIZE", 2048))
    AES_KEY_SIZE = int(os.getenv("AES_KEY_SIZE", 32))  # 32 bytes = 256-bit

    # --------------------
    # Access Control
    # --------------------
    DEFAULT_REFERRAL_EXPIRY_HOURS = int(
        os.getenv("DEFAULT_REFERRAL_EXPIRY_HOURS", 24)
    )

    # --------------------
    # Time
    # --------------------
    TIMEZONE = os.getenv("TIMEZONE", "UTC")


def validate_config():
    """
    Ensures all required configuration values are present.
    Call this once at app startup.
    """
    missing = []

    if not Config.DB_HOST:
        missing.append("DB_HOST")
    if not Config.DB_NAME:
        missing.append("DB_NAME")
    if not Config.DB_USER:
        missing.append("DB_USER")
    if not Config.DB_PASSWORD:
        missing.append("DB_PASSWORD")

    if missing:
        raise RuntimeError(
            f"Missing required environment variables: {', '.join(missing)}"
        )
