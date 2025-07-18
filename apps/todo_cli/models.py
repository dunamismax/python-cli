"""Todo models for the CLI application."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class Priority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(str, Enum):
    """Task status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TodoItem(BaseModel):
    """Todo item model."""
    
    id: int
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM
    status: Status = Status.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    
    def __str__(self) -> str:
        status_icon = {
            Status.PENDING: "⏳",
            Status.IN_PROGRESS: "🔄",
            Status.COMPLETED: "✅",
            Status.CANCELLED: "❌",
        }
        
        priority_icon = {
            Priority.LOW: "🟢",
            Priority.MEDIUM: "🟡",
            Priority.HIGH: "🔴",
        }
        
        return f"{status_icon[self.status]} {priority_icon[self.priority]} [{self.id}] {self.title}"


class TodoList(BaseModel):
    """Todo list model."""
    
    items: List[TodoItem] = Field(default_factory=list)
    next_id: int = 1
    
    def add_item(self, title: str, description: Optional[str] = None, 
                 priority: Priority = Priority.MEDIUM, 
                 due_date: Optional[datetime] = None,
                 tags: Optional[List[str]] = None) -> TodoItem:
        """Add a new todo item."""
        item = TodoItem(
            id=self.next_id,
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            tags=tags or []
        )
        self.items.append(item)
        self.next_id += 1
        return item
    
    def get_item(self, item_id: int) -> Optional[TodoItem]:
        """Get a todo item by ID."""
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def update_item(self, item_id: int, **kwargs) -> Optional[TodoItem]:
        """Update a todo item."""
        item = self.get_item(item_id)
        if item:
            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            item.updated_at = datetime.now()
            return item
        return None
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a todo item."""
        item = self.get_item(item_id)
        if item:
            self.items.remove(item)
            return True
        return False
    
    def complete_item(self, item_id: int) -> Optional[TodoItem]:
        """Mark a todo item as completed."""
        item = self.get_item(item_id)
        if item:
            item.status = Status.COMPLETED
            item.completed_at = datetime.now()
            item.updated_at = datetime.now()
            return item
        return None
    
    def filter_items(self, 
                    status: Optional[Status] = None,
                    priority: Optional[Priority] = None,
                    tag: Optional[str] = None) -> List[TodoItem]:
        """Filter todo items."""
        filtered = self.items
        
        if status:
            filtered = [item for item in filtered if item.status == status]
        
        if priority:
            filtered = [item for item in filtered if item.priority == priority]
        
        if tag:
            filtered = [item for item in filtered if tag in item.tags]
        
        return filtered
    
    def get_stats(self) -> dict:
        """Get todo list statistics."""
        total = len(self.items)
        completed = len([item for item in self.items if item.status == Status.COMPLETED])
        pending = len([item for item in self.items if item.status == Status.PENDING])
        in_progress = len([item for item in self.items if item.status == Status.IN_PROGRESS])
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "in_progress": in_progress,
            "completion_rate": (completed / total * 100) if total > 0 else 0
        }