"""
Task queue implementation for background processing.
"""

import logging
import asyncio
import uuid
from typing import Dict, Any, Callable, Awaitable, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger("manus-backend.services.task_queue")

class TaskStatus(str, Enum):
    """Task status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task:
    """Task representation."""
    
    def __init__(self, task_id: str, task_type: str, content: str, parameters: Optional[Dict[str, Any]] = None):
        self.task_id = task_id
        self.task_type = task_type
        self.content = content
        self.parameters = parameters or {}
        self.status = TaskStatus.PENDING
        self.progress = 0.0
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.completed_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "status": self.status,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
    
    def update_progress(self, progress: float):
        """Update task progress."""
        self.progress = max(0.0, min(1.0, progress))
        self.updated_at = datetime.now()
    
    def complete(self, result: Any = None):
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.progress = 1.0
        self.result = result
        self.updated_at = datetime.now()
        self.completed_at = datetime.now()
    
    def fail(self, error: str):
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.error = error
        self.updated_at = datetime.now()
        self.completed_at = datetime.now()
    
    def cancel(self):
        """Mark task as cancelled."""
        self.status = TaskStatus.CANCELLED
        self.updated_at = datetime.now()
        self.completed_at = datetime.now()

class TaskQueue:
    """Simple in-memory task queue."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.handlers: Dict[str, Callable[[Task], Awaitable[Any]]] = {}
        self.running = False
        self.worker_task = None
    
    def register_handler(self, task_type: str, handler: Callable[[Task], Awaitable[Any]]):
        """
        Register a handler for a task type.
        
        Args:
            task_type: Task type to handle.
            handler: Async function to handle the task.
        """
        self.handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type}")
    
    async def create_task(self, task_type: str, content: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new task.
        
        Args:
            task_type: Type of task.
            content: Task content.
            parameters: Additional parameters.
            
        Returns:
            Task ID.
        """
        task_id = str(uuid.uuid4())
        task = Task(task_id, task_type, content, parameters)
        self.tasks[task_id] = task
        logger.info(f"Created task: {task_id} of type: {task_type}")
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Get a task by ID.
        
        Args:
            task_id: Task ID.
            
        Returns:
            Task or None if not found.
        """
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        """
        Get all tasks.
        
        Returns:
            List of all tasks.
        """
        return list(self.tasks.values())
    
    def get_pending_tasks(self) -> List[Task]:
        """
        Get all pending tasks.
        
        Returns:
            List of pending tasks.
        """
        return [task for task in self.tasks.values() if task.status == TaskStatus.PENDING]
    
    async def process_task(self, task: Task):
        """
        Process a task.
        
        Args:
            task: Task to process.
        """
        if task.status != TaskStatus.PENDING:
            return
        
        handler = self.handlers.get(task.task_type)
        if not handler:
            task.fail(f"No handler registered for task type: {task.task_type}")
            return
        
        task.status = TaskStatus.RUNNING
        task.updated_at = datetime.now()
        
        try:
            result = await handler(task)
            task.complete(result)
        except Exception as e:
            logger.error(f"Error processing task {task.task_id}: {e}")
            task.fail(str(e))
    
    async def worker(self):
        """Worker loop to process tasks."""
        while self.running:
            pending_tasks = self.get_pending_tasks()
            if pending_tasks:
                task = pending_tasks[0]
                await self.process_task(task)
            else:
                await asyncio.sleep(1)
    
    async def start(self):
        """Start the task queue worker."""
        if self.running:
            return
        
        self.running = True
        self.worker_task = asyncio.create_task(self.worker())
        logger.info("Task queue worker started")
    
    async def stop(self):
        """Stop the task queue worker."""
        if not self.running:
            return
        
        self.running = False
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
            self.worker_task = None
        
        logger.info("Task queue worker stopped")
