"""Tests for shared utilities module."""

import pytest
import json
from pathlib import Path
from datetime import datetime
from shared.utils import (
    load_json,
    save_json,
    format_datetime,
    sanitize_filename,
    truncate_string,
    bytes_to_human,
)


def test_load_save_json(tmp_path):
    """Test JSON loading and saving."""
    data = {"key": "value", "number": 42, "list": [1, 2, 3]}
    file_path = tmp_path / "test.json"
    
    # Save JSON
    save_json(data, file_path)
    assert file_path.exists()
    
    # Load JSON
    loaded_data = load_json(file_path)
    assert loaded_data == data


def test_format_datetime():
    """Test datetime formatting."""
    dt = datetime(2023, 12, 25, 15, 30, 45)
    
    # Default format
    result = format_datetime(dt)
    assert result == "2023-12-25 15:30:45"
    
    # Custom format
    result = format_datetime(dt, "%Y-%m-%d")
    assert result == "2023-12-25"
    
    result = format_datetime(dt, "%H:%M:%S")
    assert result == "15:30:45"


def test_sanitize_filename():
    """Test filename sanitization."""
    # Test invalid characters
    assert sanitize_filename("file<name>.txt") == "file_name_.txt"
    assert sanitize_filename("file:name.txt") == "file_name.txt"
    assert sanitize_filename("file/name.txt") == "file_name.txt"
    assert sanitize_filename("file|name.txt") == "file_name.txt"
    
    # Test valid filename
    assert sanitize_filename("valid_filename.txt") == "valid_filename.txt"
    
    # Test whitespace
    assert sanitize_filename("  file name  ") == "file name"


def test_truncate_string():
    """Test string truncation."""
    # Short string
    assert truncate_string("short", 10) == "short"
    
    # Long string with default suffix
    assert truncate_string("this is a very long string", 10) == "this is..."
    
    # Long string with custom suffix
    assert truncate_string("this is a very long string", 10, "...") == "this is..."
    
    # Custom suffix
    assert truncate_string("this is a very long string", 10, " [more]") == "this [more]"


def test_bytes_to_human():
    """Test bytes to human readable format conversion."""
    assert bytes_to_human(0) == "0.0 B"
    assert bytes_to_human(512) == "512.0 B"
    assert bytes_to_human(1024) == "1.0 KB"
    assert bytes_to_human(1536) == "1.5 KB"
    assert bytes_to_human(1024 * 1024) == "1.0 MB"
    assert bytes_to_human(1024 * 1024 * 1024) == "1.0 GB"
    assert bytes_to_human(1024 * 1024 * 1024 * 1024) == "1.0 TB"


def test_load_json_file_not_found(tmp_path):
    """Test loading non-existent JSON file."""
    file_path = tmp_path / "nonexistent.json"
    
    with pytest.raises(FileNotFoundError):
        load_json(file_path)


def test_save_json_creates_directory(tmp_path):
    """Test that save_json creates parent directories."""
    data = {"test": "data"}
    file_path = tmp_path / "subdir" / "test.json"
    
    save_json(data, file_path)
    
    assert file_path.exists()
    assert file_path.parent.exists()
    
    loaded_data = load_json(file_path)
    assert loaded_data == data