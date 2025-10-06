from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
 DATABASE_URL: str
 SECRET_KEY: str
 ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200
 OCR_ENGINE: str = "tesseract"
 TESSERACT_CMD: str = "/usr/bin/tesseract"
 UPLOAD_DIR: str = "uploads"
 BETFAIR_DEFAULT_COMMISSION: float = 0.05

 DEFAULT_ADMIN_USERNAME: str = "admin"
 DEFAULT_ADMIN_PASSWORD: str = "dwang1237"
 DEFAULT_EMPLOYEE_USERNAME: str = "slave"
 DEFAULT_EMPLOYEE_PASSWORD: str = "admin"

 model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()