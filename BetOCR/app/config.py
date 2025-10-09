from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str | None = None
    SECRET_KEY: str = "dev"
    AUTH_DISABLED: bool = True  # leave True for plug-and-play (no login)

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

