"""FastAPI dependencies."""

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from shared.database import get_db_manager
from shared.config import get_config


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dependency."""
    db_manager = get_db_manager()
    async with db_manager.get_session() as session:
        yield session


def get_settings():
    """Get application settings dependency."""
    return get_config()