"""Storage utilities for the todo CLI."""

from pathlib import Path
from typing import Optional
from .models import TodoList
from shared.utils import load_json, save_json
from shared.config import get_config


class TodoStorage:
    """Handles storage and retrieval of todo lists."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path is None:
            config = get_config()
            storage_path = config.data_dir / "todo_list.json"
        
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load(self) -> TodoList:
        """Load todo list from storage."""
        if not self.storage_path.exists():
            return TodoList()
        
        try:
            data = load_json(self.storage_path)
            return TodoList(**data)
        except Exception as e:
            print(f"Error loading todo list: {e}")
            return TodoList()
    
    def save(self, todo_list: TodoList) -> None:
        """Save todo list to storage."""
        try:
            data = todo_list.model_dump()
            save_json(data, self.storage_path)
        except Exception as e:
            print(f"Error saving todo list: {e}")
    
    def backup(self) -> Optional[Path]:
        """Create a backup of the current todo list."""
        if not self.storage_path.exists():
            return None
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.storage_path.with_suffix(f".{timestamp}.backup.json")
        
        try:
            backup_path.write_text(self.storage_path.read_text())
            return backup_path
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
    
    def restore(self, backup_path: Path) -> bool:
        """Restore todo list from backup."""
        if not backup_path.exists():
            return False
        
        try:
            self.storage_path.write_text(backup_path.read_text())
            return True
        except Exception as e:
            print(f"Error restoring from backup: {e}")
            return False