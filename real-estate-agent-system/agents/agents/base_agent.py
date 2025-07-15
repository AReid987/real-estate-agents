"""
Base Agent class for all specialized agents in the system
"""

import asyncio
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()

class BaseRealEstateAgent:
    """Base class for all real estate marketing agents"""
    
    def __init__(
        self,
        name: str,
        description: str,
        system_message: str,
        **kwargs
    ):
        self.name = name
        self.description = description
        self.system_message = system_message
        self._is_active = False
        self._current_tasks = {}
        
    async def initialize(self):
        """Initialize the agent"""
        self._is_active = True
        logger.info(f"Agent {self.name} initialized")
        
    async def shutdown(self):
        """Shutdown the agent"""
        self._is_active = False
        # Cancel any running tasks
        for task_id, task in self._current_tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self._current_tasks.clear()
        logger.info(f"Agent {self.name} shutdown")
        
    @property
    def is_active(self) -> bool:
        """Check if agent is active"""
        return self._is_active
        
    async def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "active": self._is_active,
            "current_tasks": len(self._current_tasks),
            "description": self.description
        }
        
    async def execute_task(self, task_id: str, task_func, *args, **kwargs):
        """Execute a task with proper tracking"""
        if not self._is_active:
            raise RuntimeError(f"Agent {self.name} is not active")
            
        task = asyncio.create_task(task_func(*args, **kwargs))
        self._current_tasks[task_id] = task
        
        try:
            result = await task
            return result
        finally:
            self._current_tasks.pop(task_id, None)
            
    async def log_action(self, action: str, details: Dict[str, Any]):
        """Log agent actions for monitoring"""
        logger.info(
            f"Agent action",
            agent=self.name,
            action=action,
            details=details
        )