from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
import asyncio
import uuid

from src.agents.coordinator import AgentCoordinator
from src.api.dependencies import get_agent_coordinator
from src.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)

class AgentTask(BaseModel):
    """Model for agent task requests."""
    query: str
    task_type: Optional[str] = None
    context: Optional[str] = None
    use_web_search: Optional[bool] = False
    require_step_by_step: Optional[bool] = True
    preferred_agent: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "query": "Tại sao bầu trời có màu xanh?",
                "task_type": "research",
                "use_web_search": True
            }
        }

class AgentResponse(BaseModel):
    """Model for agent responses."""
    task_id: str
    answer: str
    agent_name: str
    confidence: float
    thinking_process: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None

class TaskStatus(BaseModel):
    """Model for task status responses."""
    task_id: str
    status: str
    progress: Optional[float] = None
    estimated_time_remaining: Optional[float] = None

# Track tasks with an in-memory store (in a real app, use a database)
TASKS = {}

@router.post("/query", response_model=AgentResponse)
async def process_query(
    task: AgentTask,
    coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """
    Process a query using the multiagent system.
    
    The system will select the most appropriate agent or use a specified one.
    
    Parameters:
    - task: The query and associated parameters
    
    Returns:
    - Response with answer and metadata
    """
    try:
        # Process the task with the coordinator
        task_dict = task.dict()
        result = await coordinator.process_task(task_dict)
        
        # Return the response
        return AgentResponse(
            task_id=str(uuid.uuid4()),
            answer=result.get("answer", "No answer generated"),
            agent_name=result.get("agent_name", "Unknown"),
            confidence=result.get("confidence", 0.0),
            thinking_process=result.get("reasoning_process"),
            sources=result.get("sources")
        )
    except Exception as e:
        logger.error(f"Agent processing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )

@router.post("/async-query", response_model=TaskStatus)
async def process_query_async(
    task: AgentTask,
    background_tasks: BackgroundTasks,
    coordinator: AgentCoordinator = Depends(get_agent_coordinator)
):
    """
    Process a query asynchronously using the multiagent system.
    
    The system will select the most appropriate agent or use a specified one.
    The task will be processed in the background and can be polled for status.
    
    Parameters:
    - task: The query and associated parameters
    
    Returns:
    - Task ID and initial status information
    """
    task_id = str(uuid.uuid4())
    TASKS[task_id] = {"status": "queued", "progress": 0.0}
    
    async def process_task_in_background():
        try:
            TASKS[task_id]["status"] = "processing"
            
            # Process the task
            task_dict = task.dict()
            result = await coordinator.process_task(task_dict)
            
            # Store the result
            TASKS[task_id] = {
                "status": "completed",
                "progress": 1.0,
                "result": {
                    "answer": result.get("answer", "No answer generated"),
                    "agent_name": result.get("agent_name", "Unknown"),
                    "confidence": result.get("confidence", 0.0),
                    "thinking_process": result.get("reasoning_process"),
                    "sources": result.get("sources")
                }
            }
        except Exception as e:
            logger.error(f"Background task failed: {str(e)}")
            TASKS[task_id] = {
                "status": "failed",
                "error": str(e)
            }
    
    background_tasks.add_task(process_task_in_background)
    
    return TaskStatus(
        task_id=task_id,
        status="queued",
        progress=0.0
    )

@router.get("/task/{task_id}", response_model=Dict[str, Any])
async def get_task_status(task_id: str):
    """
    Get the status of an asynchronous task.
    
    Parameters:
    - task_id: The ID of the task to check
    
    Returns:
    - Task status and result if completed
    """
    if task_id not in TASKS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    task_info = TASKS[task_id]
    
    # If the task is completed, include the result
    if task_info.get("status") == "completed":
        return {
            "task_id": task_id,
            "status": "completed",
            "result": task_info.get("result", {})
        }
    
    # For other statuses, just return the status information
    return {
        "task_id": task_id,
        "status": task_info.get("status", "unknown"),
        "progress": task_info.get("progress", 0.0),
        "error": task_info.get("error")
    } 