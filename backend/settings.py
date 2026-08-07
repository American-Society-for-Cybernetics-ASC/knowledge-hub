from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


# These are overridden by environment variables and the .env file.
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    local_deployment: bool = True
    """Set to True if this deployment is a local deployment.
    Set to False if this deployment is a production deployment."""
    testing: bool = False
    """Set to true when tests are currently executing"""

    google_username: Optional[str] = None
    google_password: Optional[str] = None

    cron_secret: str = "Local"
    """The Vercel Cron job secret"""

    # Auth Settings
    secret_key: str = ""
    """RSA private key content for JWT signing"""
    fernet_key: str = ""
    """Fernet key for encrypting TOTP secrets"""
    jwt_issuer: str = "ckh.asc-cybernetics.org"
    """JWT issuer identifier"""
    jwt_expiry_minutes: int = 10
    """JWT token expiry in minutes"""

    supabase_database_url: str = ""
    """Connection string for the production Supabase database"""


SETTINGS = Settings()
