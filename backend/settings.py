from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    local_env: bool = True

    cron_secret: str = "Local"
    """The Vercel Cron job secret"""


settings = Settings()
