from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    DATABASE_URL: str = Field(default="")
    SECRET_KEY: str = Field(default="dev-secret")

    # Toggle auth off/on via env or code; True = no login required
    AUTH_DISABLED: bool = Field(default=True)

    DEFAULT_ADMIN_USERNAME: str = Field(default="admin")
    DEFAULT_ADMIN_PASSWORD: str = Field(default="admin123")
    DEFAULT_EMPLOYEE_USERNAME: str = Field(default="employee")
    DEFAULT_EMPLOYEE_PASSWORD: str = Field(default="employee123")

    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

settings = Settings()
