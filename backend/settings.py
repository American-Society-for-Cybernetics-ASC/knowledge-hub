from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    local_deployment: bool = True
    """Set to True if this deployment is a local deployment."""
    testing: bool = False
    """Set to true when tests are currently executing"""

    cron_secret: str = "Local"
    """The Vercel Cron job secret"""

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
