from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    local_deployment: bool = True
    """Set to True if this deployment is a local deployment."""
    testing: bool = False
    """Set to true when tests are currently executing"""

    cron_secret: str = "Local"
    """The Vercel Cron job secret"""
    
    supabase_database_url: str = ""
    """Connection string for the production Supabase database"""


SETTINGS = Settings()
