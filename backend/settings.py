from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


# These are overridden by environment variables and the .env file.
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env.local"))

    local_deployment: bool = False
    """Set to True if this deployment is a local deployment.
    Set to False if this deployment is a production deployment."""
    testing: bool = False
    """Set to true when tests are currently executing"""

    google_username: Optional[str] = None
    google_password: Optional[str] = None

    # google workspace
    google_workspace_admin_email: Optional[str] = None

    # google cloud
    google_cloud_project_number: Optional[str] = None
    google_workload_identity_pool: Optional[str] = None
    google_workload_identity_provider: Optional[str] = None
    service_account_email: Optional[str] = None

    vercel_oidc_token: Optional[str] = None

    stripe_api_key: Optional[str] = None
    stripe_publishable_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None

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

    database_url: str = ""
    """Connection string for the production Supabase database"""

    backend_root_path: str = ""
    """Root path for if served behind a proxy"""


SETTINGS = Settings()
