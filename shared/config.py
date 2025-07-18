"""Configuration management using Pydantic."""

from typing import Optional
from pydantic import BaseSettings, Field
from pathlib import Path


class BaseConfig(BaseSettings):
    """Base configuration class."""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class DatabaseConfig(BaseConfig):
    """Database configuration."""
    
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/app.db",
        description="Database URL"
    )
    echo_sql: bool = Field(
        default=False,
        description="Enable SQL query logging"
    )


class APIConfig(BaseConfig):
    """API server configuration."""
    
    host: str = Field(default="127.0.0.1", description="API host")
    port: int = Field(default=8000, description="API port")
    reload: bool = Field(default=True, description="Enable auto-reload")
    debug: bool = Field(default=True, description="Enable debug mode")
    
    # Security
    secret_key: str = Field(
        default="your-secret-key-here",
        description="Secret key for JWT tokens"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration in minutes"
    )


class CeleryConfig(BaseConfig):
    """Celery configuration."""
    
    broker_url: str = Field(
        default="redis://localhost:6379/0",
        description="Celery broker URL"
    )
    result_backend: str = Field(
        default="redis://localhost:6379/0",
        description="Celery result backend URL"
    )
    task_serializer: str = Field(
        default="json",
        description="Task serializer"
    )
    result_serializer: str = Field(
        default="json",
        description="Result serializer"
    )
    accept_content: list[str] = Field(
        default=["json"],
        description="Accepted content types"
    )
    timezone: str = Field(
        default="UTC",
        description="Timezone"
    )
    enable_utc: bool = Field(
        default=True,
        description="Enable UTC"
    )


class AppConfig(BaseConfig):
    """Application configuration."""
    
    app_name: str = Field(default="Python CLI App", description="Application name")
    version: str = Field(default="0.1.0", description="Application version")
    description: str = Field(
        default="A Python CLI application",
        description="Application description"
    )
    
    # Paths
    data_dir: Path = Field(
        default=Path("./data"),
        description="Data directory"
    )
    logs_dir: Path = Field(
        default=Path("./logs"),
        description="Logs directory"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    # Database
    db: DatabaseConfig = Field(default_factory=DatabaseConfig)
    
    # API
    api: APIConfig = Field(default_factory=APIConfig)
    
    # Celery
    celery: CeleryConfig = Field(default_factory=CeleryConfig)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)


# Global configuration instance
config: Optional[AppConfig] = None


def get_config() -> AppConfig:
    """Get the global configuration instance."""
    global config
    if config is None:
        config = AppConfig()
    return config


def init_config(**kwargs) -> AppConfig:
    """Initialize the global configuration."""
    global config
    config = AppConfig(**kwargs)
    return config