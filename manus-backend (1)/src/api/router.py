"""
API router setup for the Manus Backend.
"""

import logging
from fastapi import APIRouter, FastAPI, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional

from services.provider_manager import ProviderManager

logger = logging.getLogger("manus-backend.api")

# Request and response models
class CompletionRequest(BaseModel):
    """Request model for completion generation."""
    prompt: str
    provider: Optional[str] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: bool = False

class CompletionResponse(BaseModel):
    """Response model for completion generation."""
    text: str
    provider: str
    model: str
    tokens: int
    request_id: str

class ProviderStatusResponse(BaseModel):
    """Response model for provider status."""
    providers: List[Dict[str, Any]]

class TaskRequest(BaseModel):
    """Request model for task creation."""
    task_type: str
    content: str
    parameters: Optional[Dict[str, Any]] = None

class TaskResponse(BaseModel):
    """Response model for task creation."""
    task_id: str
    status: str

class TaskStatusResponse(BaseModel):
    """Response model for task status."""
    task_id: str
    status: str
    progress: float
    result: Optional[Dict[str, Any]] = None

def setup_routes(app: FastAPI, provider_manager: ProviderManager):
    """
    Setup API routes for the application.
    
    Args:
        app: FastAPI application instance.
        provider_manager: Provider manager instance.
    """
    # Create API router
    router = APIRouter(prefix="/api/v1")
    
    # Health check endpoint
    @router.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "ok"}
    
    # Provider status endpoint
    @router.get("/providers", response_model=ProviderStatusResponse)
    async def get_provider_status():
        """Get status of all providers."""
        return {"providers": provider_manager.get_provider_status()}
    
    # Completion endpoint
    @router.post("/completions", response_model=CompletionResponse)
    async def create_completion(request: CompletionRequest):
        """
        Generate a completion for the given prompt.
        
        Args:
            request: Completion request.
            
        Returns:
            Completion response.
        """
        try:
            # Prepare kwargs for provider
            kwargs = {}
            if request.max_tokens is not None:
                kwargs["max_tokens"] = request.max_tokens
            if request.temperature is not None:
                kwargs["temperature"] = request.temperature
            
            # Generate completion
            result = await provider_manager.generate_completion(
                prompt=request.prompt,
                provider_name=request.provider,
                model=request.model,
                **kwargs
            )
            
            # Return response
            return CompletionResponse(
                text=result["text"],
                provider=result["provider"],
                model=result["model"],
                tokens=result["tokens"],
                request_id=result["request_id"]
            )
        except Exception as e:
            logger.error(f"Error generating completion: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # Task management endpoints
    @router.post("/tasks", response_model=TaskResponse)
    async def create_task(request: TaskRequest, background_tasks: BackgroundTasks):
        """
        Create a new task.
        
        Args:
            request: Task request.
            background_tasks: Background tasks.
            
        Returns:
            Task response.
        """
        # This would be implemented with a task queue system like Celery
        # For now, we'll just return a mock response
        task_id = "task_123456"
        
        # In a real implementation, we would add the task to a queue
        # background_tasks.add_task(process_task, task_id, request)
        
        return TaskResponse(task_id=task_id, status="pending")
    
    @router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
    async def get_task_status(task_id: str):
        """
        Get status of a task.
        
        Args:
            task_id: Task ID.
            
        Returns:
            Task status response.
        """
        # This would be implemented with a task queue system
        # For now, we'll just return a mock response
        return TaskStatusResponse(
            task_id=task_id,
            status="in_progress",
            progress=0.5,
            result=None
        )
    
    # Register router with app
    app.include_router(router)
    
    logger.info("API routes setup complete")
