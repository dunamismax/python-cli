"""Tests for the API server application."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api_server import schemas
from apps.api_server.main import create_app


class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_root_endpoint(self, api_client: TestClient):
        """Test the root endpoint."""
        response = api_client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
    
    def test_health_endpoint(self, api_client: TestClient):
        """Test the health check endpoint."""
        response = api_client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"


class TestUserEndpoints:
    """Test user-related endpoints."""
    
    def test_create_user(self, api_client: TestClient):
        """Test creating a new user."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True,
        }
        
        response = api_client.post("/api/v1/users/", json=user_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["full_name"] == user_data["full_name"]
        assert data["is_active"] == user_data["is_active"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_user_duplicate_username(self, api_client: TestClient):
        """Test creating a user with duplicate username."""
        user_data = {
            "username": "duplicate",
            "email": "test1@example.com",
        }
        
        # Create first user
        response1 = api_client.post("/api/v1/users/", json=user_data)
        assert response1.status_code == 201
        
        # Try to create duplicate
        user_data["email"] = "test2@example.com"
        response2 = api_client.post("/api/v1/users/", json=user_data)
        assert response2.status_code == 400
        assert "Username already registered" in response2.json()["detail"]
    
    def test_get_users(self, api_client: TestClient):
        """Test getting all users."""
        # Create a user first
        user_data = {
            "username": "listuser",
            "email": "list@example.com",
        }
        api_client.post("/api/v1/users/", json=user_data)
        
        response = api_client.get("/api/v1/users/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_user_by_id(self, api_client: TestClient):
        """Test getting a user by ID."""
        # Create a user first
        user_data = {
            "username": "getuser",
            "email": "get@example.com",
        }
        create_response = api_client.post("/api/v1/users/", json=user_data)
        created_user = create_response.json()
        
        response = api_client.get(f"/api/v1/users/{created_user['id']}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == created_user["id"]
        assert data["username"] == user_data["username"]
    
    def test_get_user_not_found(self, api_client: TestClient):
        """Test getting a non-existent user."""
        response = api_client.get("/api/v1/users/99999")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_update_user(self, api_client: TestClient):
        """Test updating a user."""
        # Create a user first
        user_data = {
            "username": "updateuser",
            "email": "update@example.com",
        }
        create_response = api_client.post("/api/v1/users/", json=user_data)
        created_user = create_response.json()
        
        # Update the user
        update_data = {
            "full_name": "Updated Name",
            "is_active": False,
        }
        response = api_client.put(f"/api/v1/users/{created_user['id']}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["full_name"] == update_data["full_name"]
        assert data["is_active"] == update_data["is_active"]
        assert data["username"] == user_data["username"]  # Should remain unchanged
    
    def test_delete_user(self, api_client: TestClient):
        """Test deleting a user."""
        # Create a user first
        user_data = {
            "username": "deleteuser",
            "email": "delete@example.com",
        }
        create_response = api_client.post("/api/v1/users/", json=user_data)
        created_user = create_response.json()
        
        # Delete the user
        response = api_client.delete(f"/api/v1/users/{created_user['id']}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify user is deleted
        get_response = api_client.get(f"/api/v1/users/{created_user['id']}")
        assert get_response.status_code == 404


class TestTaskEndpoints:
    """Test task-related endpoints."""
    
    def test_create_task(self, api_client: TestClient):
        """Test creating a new task."""
        task_data = {
            "title": "Test Task",
            "description": "This is a test task",
            "priority": "high",
            "completed": False,
        }
        
        response = api_client.post("/api/v1/tasks/", json=task_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["description"] == task_data["description"]
        assert data["priority"] == task_data["priority"]
        assert data["completed"] == task_data["completed"]
        assert "id" in data
        assert "created_at" in data
    
    def test_get_tasks(self, api_client: TestClient):
        """Test getting all tasks."""
        # Create a task first
        task_data = {
            "title": "List Task",
            "description": "Task for listing",
        }
        api_client.post("/api/v1/tasks/", json=task_data)
        
        response = api_client.get("/api/v1/tasks/")
        assert response.status_code == 200
        
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "pages" in data
        assert isinstance(data["tasks"], list)
        assert len(data["tasks"]) >= 1
    
    def test_get_tasks_with_filters(self, api_client: TestClient):
        """Test getting tasks with filters."""
        # Create tasks with different properties
        high_task = {
            "title": "High Priority Task",
            "priority": "high",
            "completed": False,
        }
        completed_task = {
            "title": "Completed Task",
            "priority": "medium",
            "completed": True,
        }
        
        api_client.post("/api/v1/tasks/", json=high_task)
        api_client.post("/api/v1/tasks/", json=completed_task)
        
        # Filter by priority
        response = api_client.get("/api/v1/tasks/?priority=high")
        assert response.status_code == 200
        data = response.json()
        assert all(task["priority"] == "high" for task in data["tasks"])
        
        # Filter by completed status
        response = api_client.get("/api/v1/tasks/?completed=true")
        assert response.status_code == 200
        data = response.json()
        assert all(task["completed"] is True for task in data["tasks"])
    
    def test_complete_task(self, api_client: TestClient):
        """Test completing a task."""
        # Create a task first
        task_data = {
            "title": "Task to Complete",
            "completed": False,
        }
        create_response = api_client.post("/api/v1/tasks/", json=task_data)
        created_task = create_response.json()
        
        # Complete the task
        response = api_client.post(f"/api/v1/tasks/{created_task['id']}/complete")
        assert response.status_code == 200
        
        data = response.json()
        assert data["completed"] is True
    
    def test_task_not_found(self, api_client: TestClient):
        """Test operations on non-existent task."""
        response = api_client.get("/api/v1/tasks/99999")
        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]


class TestSchemas:
    """Test Pydantic schemas."""
    
    def test_user_create_schema(self):
        """Test UserCreate schema validation."""
        # Valid data
        valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True,
        }
        user = schemas.UserCreate(**valid_data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
        
        # Test with minimal data
        minimal_data = {
            "username": "minimal",
            "email": "minimal@example.com",
        }
        user = schemas.UserCreate(**minimal_data)
        assert user.username == "minimal"
        assert user.email == "minimal@example.com"
        assert user.full_name is None
        assert user.is_active is True  # Default value
    
    def test_task_create_schema(self):
        """Test TaskCreate schema validation."""
        # Valid data
        valid_data = {
            "title": "Test Task",
            "description": "Test description",
            "priority": "high",
            "completed": False,
        }
        task = schemas.TaskCreate(**valid_data)
        assert task.title == "Test Task"
        assert task.description == "Test description"
        assert task.priority == "high"
        assert task.completed is False
        
        # Test with minimal data
        minimal_data = {
            "title": "Minimal Task",
        }
        task = schemas.TaskCreate(**minimal_data)
        assert task.title == "Minimal Task"
        assert task.description is None
        assert task.priority == "medium"  # Default value
        assert task.completed is False  # Default value
    
    def test_schema_validation_errors(self):
        """Test schema validation errors."""
        # Test UserCreate with invalid data
        with pytest.raises(ValueError):
            schemas.UserCreate(username="", email="invalid-email")
        
        # Test TaskCreate with invalid priority
        with pytest.raises(ValueError):
            schemas.TaskCreate(title="Test", priority="invalid")