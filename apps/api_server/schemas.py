"""Pydantic schemas for the API server."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema."""
    
    username: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=1, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = Field(None, min_length=1, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class User(UserBase):
    """User response schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class TaskBase(BaseModel):
    """Base task schema."""
    
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    completed: bool = False
    priority: str = Field(default="medium", regex="^(low|medium|high)$")


class TaskCreate(TaskBase):
    """Schema for creating a task."""
    pass


class TaskUpdate(BaseModel):
    """Schema for updating a task."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = Field(None, regex="^(low|medium|high)$")


class Task(TaskBase):
    """Task response schema."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class TaskList(BaseModel):
    """Task list response schema."""
    
    tasks: list[Task]
    total: int
    page: int
    per_page: int
    pages: int


class Message(BaseModel):
    """Generic message response."""
    
    message: str


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    error: str
    details: Optional[str] = None