"""
Configuration management for Nexus ADK Platform.
"""
import os
from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""
    host: str = Field(default="localhost", alias="POSTGRES_HOST")
    port: int = Field(default=5432, alias="POSTGRES_PORT")
    database: str = Field(default="nexusdb", alias="POSTGRES_DB")
    username: str = Field(default="nexususer", alias="POSTGRES_USER")
    password: str = Field(default="", alias="POSTGRES_PASSWORD")

    @property
    def connection_string(self) -> str:
        """Get SQLAlchemy connection string."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

    @property
    def psycopg2_string(self) -> str:
        """Get psycopg2 connection string."""
        return f"host={self.host} port={self.port} dbname={self.database} user={self.username} password={self.password}"


class SecurityConfig(BaseSettings):
    """Security and guardrails configuration."""
    secret_key: str = Field(default="dev-secret-key", alias="SECRET_KEY")
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        alias="ALLOWED_ORIGINS"
    )
    enable_guardrails: bool = Field(default=True, alias="ENABLE_GUARDRAILS")
    blocked_topics: List[str] = Field(
        default=["jailbreak", "harmful_content", "pii"],
        alias="BLOCKED_TOPICS"
    )
    allowed_operations: List[str] = Field(
        default=["SELECT", "INSERT", "UPDATE", "DELETE"],
        alias="ALLOWED_OPERATIONS"
    )


class GoogleConfig(BaseSettings):
    """Google ADK and Gemini configuration."""
    api_key: str = Field(default="", alias="GOOGLE_API_KEY")
    model: str = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL")
    maps_api_key: str = Field(default="", alias="GOOGLE_MAPS_API_KEY")


class AppConfig(BaseSettings):
    """Main application configuration."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    host: str = Field(default="0.0.0.0", alias="APP_HOST")
    port: int = Field(default=8000, alias="APP_PORT")
    debug: bool = Field(default=True, alias="DEBUG")

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)
    google: GoogleConfig = Field(default_factory=GoogleConfig)

    chroma_persist_dir: str = Field(default="./chroma_data", alias="CHROMA_PERSIST_DIR")


@lru_cache()
def get_settings() -> AppConfig:
    """Get cached application settings."""
    return AppConfig()


# Global settings instance
settings = get_settings()
