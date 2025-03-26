"""
API route tests for the Manus Backend.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from main import app, initialize_app
from services.provider_manager import ProviderManager

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    # Initialize the app
    initialize_app()
    
    # Create test client
    client = TestClient(app)
    return client

@pytest.fixture
def mock_provider_manager():
    """Create a mock provider manager."""
    with patch('services.provider_manager.ProviderManager') as mock:
        # Setup mock methods
        manager_instance = mock.return_value
        manager_instance.get_provider_status.return_value = [
            {
                "name": "openai",
                "enabled": True,
                "priority": 1,
                "models": ["gpt-4o", "gpt-3.5-turbo"],
                "error_count": 0,
                "request_count": 0
            },
            {
                "name": "anthropic",
                "enabled": True,
                "priority": 2,
                "models": ["claude-3-opus", "claude-3-haiku"],
                "error_count": 0,
                "request_count": 0
            }
        ]
        
        manager_instance.generate_completion = AsyncMock(return_value={
            "text": "This is a test response",
            "provider": "openai",
            "model": "gpt-4o",
            "tokens": 10,
            "request_id": "test-request-id"
        })
        
        yield manager_instance

def test_health_check(test_client):
    """Test the health check endpoint."""
    response = test_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_provider_status(test_client, mock_provider_manager):
    """Test getting provider status."""
    response = test_client.get("/api/v1/providers")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    assert len(data["providers"]) == 2
    assert data["providers"][0]["name"] == "openai"
    assert data["providers"][1]["name"] == "anthropic"

@pytest.mark.asyncio
async def test_create_completion(test_client, mock_provider_manager):
    """Test creating a completion."""
    response = test_client.post(
        "/api/v1/completions",
        json={
            "prompt": "Test prompt",
            "provider": "openai",
            "model": "gpt-4o",
            "max_tokens": 100,
            "temperature": 0.5
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "This is a test response"
    assert data["provider"] == "openai"
    assert data["model"] == "gpt-4o"
    
    # Verify the mock was called with correct parameters
    mock_provider_manager.generate_completion.assert_called_once()
    args, kwargs = mock_provider_manager.generate_completion.call_args
    assert kwargs["prompt"] == "Test prompt"
    assert kwargs["provider_name"] == "openai"
    assert kwargs["model"] == "gpt-4o"
    assert kwargs["max_tokens"] == 100
    assert kwargs["temperature"] == 0.5

def test_create_task(test_client):
    """Test creating a task."""
    response = test_client.post(
        "/api/v1/tasks",
        json={
            "task_type": "test_task",
            "content": "Test content",
            "parameters": {"param1": "value1"}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"

def test_get_task_status(test_client):
    """Test getting task status."""
    response = test_client.get("/api/v1/tasks/task_123456")
    
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "task_123456"
    assert data["status"] == "in_progress"
    assert data["progress"] == 0.5
