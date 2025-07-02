from urllib.parse import quote_plus

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from dataclasses import dataclass
from pathlib import Path
from time import time
from typing import List

from logger import LoggerBuilder
from utils import StringBuilder

logger = LoggerBuilder("CONFIG").add_stream_handler().build()


class ConfigBase(BaseSettings):
    """Base configuration class for shared settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @classmethod
    def load(cls) -> "ConfigBase":
        """Load configuration from environment or .env file."""
        return cls()


class DatabaseSettings(ConfigBase):
    """Database configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="db_",
    )

    name: str = Field(..., min_length=1, description="Database name")
    user: Optional[str] = Field(..., min_length=1, description="Database user")
    password: Optional[str] = Field(..., min_length=1, description="Database password")
    host: Optional[str] = Field(default="localhost", description="Database host")
    port: Optional[str] = Field(default=5432, description="Database port")
    driver: Optional[str] = Field(default="aiosqlite", description="Database driver")

    @field_validator("name", "user", "password")
    @classmethod
    def non_empty(cls, v: str) -> str:
        """Ensure fields are non-empty and stripped of whitespace."""
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

    @property
    def postgresql_url(self) -> str:
        """Generate PostgreSQL connection URL with URL-encoded credentials."""
        encoded_user = quote_plus(self.user)
        encoded_password = quote_plus(self.password)
        return f"postgresql+{self.driver}://{encoded_user}:{encoded_password}@{self.host}:{self.port}/{self.name}"

    @property
    def sqlite_url(self) -> str:
        """Generate SQLite connection URL."""
        if self.driver != "aiosqlite":
            raise ValueError("SQLite URL requires 'aiosqlite' driver")
        return f"sqlite+aiosqlite:///{self.name}"


class TelegramSettings(ConfigBase):
    """Telegram bot configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_prefix="telegram_",
    )

    bot_token: str = Field(..., min_length=10, description="Telegram bot token")

    @field_validator("bot_token")
    @classmethod
    def validate_bot_token(cls, v: str) -> str:
        """Validate Telegram bot token format."""
        if not v.startswith("bot") and ":" not in v:
            raise ValueError("Invalid Telegram bot token format")
        return v.strip()


def load_settings() -> tuple[DatabaseSettings, TelegramSettings]:
    """Load all application settings."""
    return DatabaseSettings.load(), TelegramSettings.load()


@dataclass
class AdminConfig:
    admin_ids: List[int]
    config_path: Path = Path("./admin_ids.txt")
    cache_time: int = 3600

    def __post_init__(self):
        self._last_updated = 0
        self._load_admin_ids()

    def _load_admin_ids(self) -> None:
        try:
            if self.config_path.exists():
                with open(self.config_path, "r", encoding="utf-8") as f:
                    ids = f.readline().strip().split(",")
                    self.admin_ids = [int(x) for x in ids if x.strip()]
                    self._last_updated = time()
                    builder = StringBuilder()
                    for i, admin_id in enumerate(ids, 1):
                        builder.append(f"{i}. {admin_id}, ")

                    logger.info(f"Admins ids: {builder.to_string()}")

        except Exception as e:
            logger.error(f"Failed to load admin IDs: {e}")
            raise

    def is_admin(self, user_id: int) -> bool:
        if time() - self._last_updated > self.cache_time:
            self._load_admin_ids()

        return user_id in self.admin_ids
