"""Tests for shared configuration module."""

import pytest
from pathlib import Path
from shared.config import AppConfig, get_config, init_config


def test_app_config_defaults():
    """Test that AppConfig has sensible defaults."""
    config = AppConfig()
    
    assert config.app_name == "Python CLI App"
    assert config.version == "0.1.0"
    assert config.data_dir == Path("./data")
    assert config.logs_dir == Path("./logs")
    assert config.log_level == "INFO"
    assert config.db.database_url == "sqlite+aiosqlite:///./data/app.db"
    assert config.api.host == "127.0.0.1"
    assert config.api.port == 8000


def test_app_config_custom_values():
    """Test that AppConfig accepts custom values."""
    config = AppConfig(
        app_name="Custom App",
        version="1.0.0",
        data_dir="/custom/data",
        logs_dir="/custom/logs",
        log_level="DEBUG",
        db__database_url="postgresql://user:pass@localhost/db",
        api__host="0.0.0.0",
        api__port=9000,
    )
    
    assert config.app_name == "Custom App"
    assert config.version == "1.0.0"
    assert config.data_dir == Path("/custom/data")
    assert config.logs_dir == Path("/custom/logs")
    assert config.log_level == "DEBUG"
    assert config.db.database_url == "postgresql://user:pass@localhost/db"
    assert config.api.host == "0.0.0.0"
    assert config.api.port == 9000


def test_get_config_singleton():
    """Test that get_config returns the same instance."""
    config1 = get_config()
    config2 = get_config()
    
    assert config1 is config2


def test_init_config():
    """Test that init_config creates a new configuration."""
    config = init_config(app_name="Test App", version="2.0.0")
    
    assert config.app_name == "Test App"
    assert config.version == "2.0.0"
    
    # Should return the same instance on subsequent calls
    config2 = get_config()
    assert config is config2