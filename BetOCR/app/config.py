from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # accept .env, ignore unknown vars, keep env names case-insensitive
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
        env_prefix=""
    )

    # required for DB and app
    DATABASE_URL: str = Field(..., alias="DATABASE_URL")
    SECRET_KEY: str = Field("change-me", alias="SECRET_KEY")

    # auth toggle (we can run without login)
    AUTH_DISABLED: bool = Field(True, alias="AUTH_DISABLED")

    # keep your existing env names working (aliases match your Render vars)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(43200, alias="access_token_expire_minutes")
    OCR_ENGINE: str = Field("tesseract", alias="ocr_engine")
    TESSERACT_CMD: str = Field("/usr/bin/tesseract", alias="tesseract_cmd")
    UPLOAD_DIR: str = Field("uploads", alias="upload_dir")
    BETFAIR_DEFAULT_COMMISSION: float = Field(0.05, alias="betfair_default_commission")

    # seeding defaults (won’t be used if you disabled auth, but harmless)
    DEFAULT_ADMIN_USERNAME: str = Field("admin", alias="default_admin_username")
    DEFAULT_ADMIN_PASSWORD: str = Field("admin", alias="default_admin_password")
    DEFAULT_EMPLOYEE_USERNAME: str = Field("employee", alias="default_employee_username")
    DEFAULT_EMPLOYEE_PASSWORD: str = Field("employee", alias="default_employee_password")

# export singleton
settings = Settings()
