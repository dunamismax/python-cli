"""User API routes."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas, crud
from ..dependencies import get_database

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_database)
):
    """Create a new user."""
    # Check if user already exists
    existing_user = await crud.UserCRUD.get_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    existing_email = await crud.UserCRUD.get_by_email(db, user.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return await crud.UserCRUD.create(db, user)


@router.get("/", response_model=List[schemas.User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_database)
):
    """Get all users."""
    return await crud.UserCRUD.get_all(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=schemas.User)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Get a user by ID."""
    user = await crud.UserCRUD.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: AsyncSession = Depends(get_database)
):
    """Update a user."""
    user = await crud.UserCRUD.update(db, user_id, user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.delete("/{user_id}", response_model=schemas.Message)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_database)
):
    """Delete a user."""
    success = await crud.UserCRUD.delete(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return schemas.Message(message="User deleted successfully")