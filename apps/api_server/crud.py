"""CRUD operations for the API server."""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from . import models, schemas


class UserCRUD:
    """CRUD operations for users."""
    
    @staticmethod
    async def create(
        db: AsyncSession, user: schemas.UserCreate
    ) -> models.User:
        """Create a new user."""
        db_user = models.User(**user.model_dump())
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession, user_id: int
    ) -> Optional[models.User]:
        """Get user by ID."""
        result = await db.execute(
            select(models.User).where(models.User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_username(
        db: AsyncSession, username: str
    ) -> Optional[models.User]:
        """Get user by username."""
        result = await db.execute(
            select(models.User).where(models.User.username == username)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(
        db: AsyncSession, email: str
    ) -> Optional[models.User]:
        """Get user by email."""
        result = await db.execute(
            select(models.User).where(models.User.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(
        db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[models.User]:
        """Get all users with pagination."""
        result = await db.execute(
            select(models.User).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    async def update(
        db: AsyncSession, user_id: int, user_update: schemas.UserUpdate
    ) -> Optional[models.User]:
        """Update a user."""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        await db.commit()
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def delete(
        db: AsyncSession, user_id: int
    ) -> bool:
        """Delete a user."""
        db_user = await UserCRUD.get_by_id(db, user_id)
        if not db_user:
            return False
        
        await db.delete(db_user)
        await db.commit()
        return True


class TaskCRUD:
    """CRUD operations for tasks."""
    
    @staticmethod
    async def create(
        db: AsyncSession, task: schemas.TaskCreate
    ) -> models.Task:
        """Create a new task."""
        db_task = models.Task(**task.model_dump())
        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return db_task
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession, task_id: int
    ) -> Optional[models.Task]:
        """Get task by ID."""
        result = await db.execute(
            select(models.Task).where(models.Task.id == task_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        completed: Optional[bool] = None,
        priority: Optional[str] = None
    ) -> tuple[List[models.Task], int]:
        """Get all tasks with pagination and filters."""
        query = select(models.Task)
        
        if completed is not None:
            query = query.where(models.Task.completed == completed)
        
        if priority is not None:
            query = query.where(models.Task.priority == priority)
        
        # Get total count
        count_query = select(func.count(models.Task.id))
        if completed is not None:
            count_query = count_query.where(models.Task.completed == completed)
        if priority is not None:
            count_query = count_query.where(models.Task.priority == priority)
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Get tasks with pagination
        result = await db.execute(
            query.order_by(models.Task.created_at.desc()).offset(skip).limit(limit)
        )
        tasks = result.scalars().all()
        
        return tasks, total
    
    @staticmethod
    async def update(
        db: AsyncSession, task_id: int, task_update: schemas.TaskUpdate
    ) -> Optional[models.Task]:
        """Update a task."""
        db_task = await TaskCRUD.get_by_id(db, task_id)
        if not db_task:
            return None
        
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        await db.commit()
        await db.refresh(db_task)
        return db_task
    
    @staticmethod
    async def delete(
        db: AsyncSession, task_id: int
    ) -> bool:
        """Delete a task."""
        db_task = await TaskCRUD.get_by_id(db, task_id)
        if not db_task:
            return False
        
        await db.delete(db_task)
        await db.commit()
        return True