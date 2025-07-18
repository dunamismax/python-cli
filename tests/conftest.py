"""Pytest configuration and fixtures."""

import asyncio
import pytest
from pathlib import Path
import tempfile
import shutil
from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient

from shared.config import init_config, AppConfig
from shared.database import init_db_manager, get_db_manager
from apps.api_server.main import create_app
from apps.todo_cli.models import TodoList
from apps.todo_cli.storage import TodoStorage


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(scope="session")
def test_config(temp_dir: Path) -> AppConfig:
    """Create a test configuration."""
    config = init_config(
        app_name="Test App",
        data_dir=temp_dir / "data",
        logs_dir=temp_dir / "logs",
        db__database_url=f"sqlite+aiosqlite:///{temp_dir}/test.db",
        api__host="127.0.0.1",
        api__port=8001,
        api__reload=False,
        api__debug=False,
        log_level="DEBUG",
    )
    return config


@pytest.fixture(scope="session")
async def db_manager(test_config: AppConfig):
    """Create a database manager for testing."""
    manager = init_db_manager(test_config.db.database_url)
    await manager.create_tables()
    yield manager
    await manager.close()


@pytest.fixture
async def db_session(db_manager) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    async with db_manager.get_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def api_client(test_config: AppConfig) -> TestClient:
    """Create a test client for the API."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def todo_storage(temp_dir: Path) -> TodoStorage:
    """Create a todo storage instance for testing."""
    storage_path = temp_dir / "test_todo.json"
    return TodoStorage(storage_path)


@pytest.fixture
def sample_todo_list() -> TodoList:
    """Create a sample todo list for testing."""
    from apps.todo_cli.models import Priority, Status
    
    todo_list = TodoList()
    todo_list.add_item("Test Task 1", "Description 1", Priority.HIGH)
    todo_list.add_item("Test Task 2", "Description 2", Priority.MEDIUM)
    todo_list.add_item("Test Task 3", "Description 3", Priority.LOW)
    
    # Complete one task
    todo_list.complete_item(2)
    
    return todo_list


@pytest.fixture
def sample_files_dir(temp_dir: Path) -> Path:
    """Create a directory with sample files for testing."""
    files_dir = temp_dir / "sample_files"
    files_dir.mkdir()
    
    # Create various file types
    (files_dir / "document.txt").write_text("This is a text document")
    (files_dir / "image.jpg").write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF")
    (files_dir / "script.py").write_text("print('Hello, world!')")
    (files_dir / "data.csv").write_text("name,age\nJohn,25\nJane,30")
    (files_dir / "archive.zip").write_bytes(b"PK\x03\x04")
    
    # Create a subdirectory
    sub_dir = files_dir / "subdir"
    sub_dir.mkdir()
    (sub_dir / "nested_file.txt").write_text("Nested content")
    
    return files_dir


@pytest.fixture
def duplicate_files_dir(temp_dir: Path) -> Path:
    """Create a directory with duplicate files for testing."""
    files_dir = temp_dir / "duplicate_files"
    files_dir.mkdir()
    
    # Create duplicate files
    content = "This is duplicate content"
    (files_dir / "file1.txt").write_text(content)
    (files_dir / "file2.txt").write_text(content)
    (files_dir / "file3.txt").write_text(content)
    
    # Create a unique file
    (files_dir / "unique.txt").write_text("This is unique content")
    
    return files_dir