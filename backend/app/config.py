from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=5, le=1440)

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_DIR / ".env"), str(REPO_ROOT / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
