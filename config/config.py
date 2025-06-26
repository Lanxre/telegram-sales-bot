from urllib.parse import quote_plus

from typing import Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    driver: Optional[str] = Field(default="asyncpg", description="Database driver")

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
