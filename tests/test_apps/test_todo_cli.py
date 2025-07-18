"""Tests for the todo CLI application."""

import pytest
from datetime import datetime
from pathlib import Path

from apps.todo_cli.models import TodoList, TodoItem, Priority, Status
from apps.todo_cli.storage import TodoStorage


class TestTodoItem:
    """Test TodoItem model."""
    
    def test_todo_item_creation(self):
        """Test creating a TodoItem."""
        item = TodoItem(
            id=1,
            title="Test Task",
            description="Test description",
            priority=Priority.HIGH,
            status=Status.PENDING,
        )
        
        assert item.id == 1
        assert item.title == "Test Task"
        assert item.description == "Test description"
        assert item.priority == Priority.HIGH
        assert item.status == Status.PENDING
        assert item.created_at is not None
        assert item.updated_at is None
        assert item.completed_at is None
        assert item.due_date is None
        assert item.tags == []
    
    def test_todo_item_str_representation(self):
        """Test string representation of TodoItem."""
        item = TodoItem(
            id=1,
            title="Test Task",
            priority=Priority.HIGH,
            status=Status.PENDING,
        )
        
        str_repr = str(item)
        assert "Test Task" in str_repr
        assert "[1]" in str_repr
        assert "⏳" in str_repr  # Pending icon
        assert "🔴" in str_repr  # High priority icon


class TestTodoList:
    """Test TodoList model."""
    
    def test_empty_todo_list(self):
        """Test creating an empty TodoList."""
        todo_list = TodoList()
        
        assert todo_list.items == []
        assert todo_list.next_id == 1
    
    def test_add_item(self):
        """Test adding items to TodoList."""
        todo_list = TodoList()
        
        item1 = todo_list.add_item("Task 1", "Description 1", Priority.HIGH)
        assert item1.id == 1
        assert item1.title == "Task 1"
        assert item1.description == "Description 1"
        assert item1.priority == Priority.HIGH
        assert len(todo_list.items) == 1
        assert todo_list.next_id == 2
        
        item2 = todo_list.add_item("Task 2")
        assert item2.id == 2
        assert item2.title == "Task 2"
        assert item2.priority == Priority.MEDIUM  # Default
        assert len(todo_list.items) == 2
        assert todo_list.next_id == 3
    
    def test_get_item(self):
        """Test getting items from TodoList."""
        todo_list = TodoList()
        item = todo_list.add_item("Test Task")
        
        retrieved_item = todo_list.get_item(item.id)
        assert retrieved_item is item
        
        # Test non-existent item
        assert todo_list.get_item(999) is None
    
    def test_update_item(self):
        """Test updating items in TodoList."""
        todo_list = TodoList()
        item = todo_list.add_item("Original Title", priority=Priority.LOW)
        
        updated_item = todo_list.update_item(
            item.id, 
            title="Updated Title", 
            priority=Priority.HIGH
        )
        
        assert updated_item is item
        assert updated_item.title == "Updated Title"
        assert updated_item.priority == Priority.HIGH
        assert updated_item.updated_at is not None
        
        # Test non-existent item
        assert todo_list.update_item(999, title="New Title") is None
    
    def test_delete_item(self):
        """Test deleting items from TodoList."""
        todo_list = TodoList()
        item = todo_list.add_item("Test Task")
        
        assert len(todo_list.items) == 1
        
        success = todo_list.delete_item(item.id)
        assert success is True
        assert len(todo_list.items) == 0
        
        # Test non-existent item
        assert todo_list.delete_item(999) is False
    
    def test_complete_item(self):
        """Test completing items in TodoList."""
        todo_list = TodoList()
        item = todo_list.add_item("Test Task")
        
        assert item.status == Status.PENDING
        assert item.completed_at is None
        
        completed_item = todo_list.complete_item(item.id)
        assert completed_item is item
        assert completed_item.status == Status.COMPLETED
        assert completed_item.completed_at is not None
        assert completed_item.updated_at is not None
        
        # Test non-existent item
        assert todo_list.complete_item(999) is None
    
    def test_filter_items(self):
        """Test filtering items in TodoList."""
        todo_list = TodoList()
        
        # Add items with different properties
        item1 = todo_list.add_item("Task 1", priority=Priority.HIGH, tags=["work"])
        item2 = todo_list.add_item("Task 2", priority=Priority.LOW, tags=["personal"])
        item3 = todo_list.add_item("Task 3", priority=Priority.HIGH, tags=["work", "urgent"])
        
        # Complete one item
        todo_list.complete_item(item2.id)
        
        # Filter by status
        pending_items = todo_list.filter_items(status=Status.PENDING)
        assert len(pending_items) == 2
        assert item1 in pending_items
        assert item3 in pending_items
        
        completed_items = todo_list.filter_items(status=Status.COMPLETED)
        assert len(completed_items) == 1
        assert item2 in completed_items
        
        # Filter by priority
        high_priority_items = todo_list.filter_items(priority=Priority.HIGH)
        assert len(high_priority_items) == 2
        assert item1 in high_priority_items
        assert item3 in high_priority_items
        
        # Filter by tag
        work_items = todo_list.filter_items(tag="work")
        assert len(work_items) == 2
        assert item1 in work_items
        assert item3 in work_items
        
        urgent_items = todo_list.filter_items(tag="urgent")
        assert len(urgent_items) == 1
        assert item3 in urgent_items
    
    def test_get_stats(self):
        """Test getting statistics from TodoList."""
        todo_list = TodoList()
        
        # Empty list
        stats = todo_list.get_stats()
        assert stats["total"] == 0
        assert stats["completed"] == 0
        assert stats["pending"] == 0
        assert stats["in_progress"] == 0
        assert stats["completion_rate"] == 0
        
        # Add items
        item1 = todo_list.add_item("Task 1")
        item2 = todo_list.add_item("Task 2")
        item3 = todo_list.add_item("Task 3")
        item4 = todo_list.add_item("Task 4")
        
        # Complete and update some items
        todo_list.complete_item(item1.id)
        todo_list.complete_item(item2.id)
        todo_list.update_item(item3.id, status=Status.IN_PROGRESS)
        
        stats = todo_list.get_stats()
        assert stats["total"] == 4
        assert stats["completed"] == 2
        assert stats["pending"] == 1
        assert stats["in_progress"] == 1
        assert stats["completion_rate"] == 50.0


class TestTodoStorage:
    """Test TodoStorage class."""
    
    def test_save_and_load(self, tmp_path):
        """Test saving and loading TodoList."""
        storage_path = tmp_path / "test_todo.json"
        storage = TodoStorage(storage_path)
        
        # Create a todo list
        todo_list = TodoList()
        todo_list.add_item("Task 1", "Description 1", Priority.HIGH)
        todo_list.add_item("Task 2", "Description 2", Priority.LOW)
        
        # Save
        storage.save(todo_list)
        assert storage_path.exists()
        
        # Load
        loaded_list = storage.load()
        assert len(loaded_list.items) == 2
        assert loaded_list.items[0].title == "Task 1"
        assert loaded_list.items[0].description == "Description 1"
        assert loaded_list.items[0].priority == Priority.HIGH
        assert loaded_list.items[1].title == "Task 2"
        assert loaded_list.next_id == 3
    
    def test_load_nonexistent_file(self, tmp_path):
        """Test loading from non-existent file."""
        storage_path = tmp_path / "nonexistent.json"
        storage = TodoStorage(storage_path)
        
        # Should return empty TodoList
        todo_list = storage.load()
        assert isinstance(todo_list, TodoList)
        assert len(todo_list.items) == 0
        assert todo_list.next_id == 1
    
    def test_backup_and_restore(self, tmp_path):
        """Test backup and restore functionality."""
        storage_path = tmp_path / "test_todo.json"
        storage = TodoStorage(storage_path)
        
        # Create and save a todo list
        todo_list = TodoList()
        todo_list.add_item("Original Task")
        storage.save(todo_list)
        
        # Create backup
        backup_path = storage.backup()
        assert backup_path is not None
        assert backup_path.exists()
        assert ".backup.json" in backup_path.name
        
        # Modify the original
        todo_list.add_item("Modified Task")
        storage.save(todo_list)
        
        # Restore from backup
        success = storage.restore(backup_path)
        assert success is True
        
        # Verify restoration
        restored_list = storage.load()
        assert len(restored_list.items) == 1
        assert restored_list.items[0].title == "Original Task"
    
    def test_backup_nonexistent_file(self, tmp_path):
        """Test backup of non-existent file."""
        storage_path = tmp_path / "nonexistent.json"
        storage = TodoStorage(storage_path)
        
        backup_path = storage.backup()
        assert backup_path is None
    
    def test_restore_nonexistent_backup(self, tmp_path):
        """Test restore from non-existent backup."""
        storage_path = tmp_path / "test_todo.json"
        storage = TodoStorage(storage_path)
        
        backup_path = tmp_path / "nonexistent_backup.json"
        success = storage.restore(backup_path)
        assert success is False