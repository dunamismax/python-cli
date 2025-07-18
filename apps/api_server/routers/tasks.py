"""Task API routes."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import math

from .. import schemas, crud
from ..dependencies import get_database

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=schemas.Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: schemas.TaskCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new task."""
    return await crud.TaskCRUD.create(db, task)


@router.get("/", response_model=schemas.TaskList)
async def get_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    completed: Optional[bool] = None,
    priority: Optional[str] = Query(None, regex="^(low|medium|high)$"),
    db: AsyncSession = Depends(get_database)
):
    """Get all tasks with pagination and filters."""
    tasks, total = await crud.TaskCRUD.get_all(
        db, 
        skip=skip, 
        limit=limit,
        completed=completed,
        priority=priority
    )
    
    # Calculate pagination info
    page = (skip // limit) + 1
    pages = math.ceil(total / limit)
    
    return schemas.TaskList(
        tasks=tasks,
        total=total,
        page=page,
        per_page=limit,
        pages=pages
    )


@router.get("/{task_id}", response_model=schemas.Task)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Get a task by ID."""
    task = await crud.TaskCRUD.get_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.put("/{task_id}", response_model=schemas.Task)
async def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update a task."""
    task = await crud.TaskCRUD.update(db, task_id, task_update)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.delete("/{task_id}", response_model=schemas.Message)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Delete a task."""
    success = await crud.TaskCRUD.delete(db, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return schemas.Message(message="Task deleted successfully")


@router.post("/{task_id}/complete", response_model=schemas.Task)
async def complete_task(
    task_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Mark a task as completed."""
    task_update = schemas.TaskUpdate(completed=True)
    task = await crud.TaskCRUD.update(db, task_id, task_update)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.post("/{task_id}/uncomplete", response_model=schemas.Task)
async def uncomplete_task(
    task_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Mark a task as not completed."""
    task_update = schemas.TaskUpdate(completed=False)
    task = await crud.TaskCRUD.update(db, task_id, task_update)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task