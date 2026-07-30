from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    local_deployment: bool = True
    """Set to True if this deployment is a local deployment."""
    testing: bool = False
    """Set to true when tests are currently executing"""

    cron_secret: str = "Local"
    """The Vercel Cron job secret"""

    #Auth Settings
    secret_key: str = ""
    """RSA private key content for JWT signing"""
    fernet_key: str = ""
    """Fernet key for encrypting TOTP secrets"""
    jwt_issuer: str = "ckh.asc-cybernetics.org"
    """JWT issuer identifier"""
    jwt_expiry_minutes: int = 10
    """JWT token expiry in minutes"""

    model_config = SettingsConfigDict(env_file=".env")

SETTINGS = Settings()