"""Core data models and schemas."""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class MessageRole(str, Enum):
    """Roles for messages in a conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"

class Message(BaseModel):
    """Model representing a message in a conversation."""
    role: MessageRole
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True

class HistoryItem(BaseModel):
    """Model representing an item in conversation history."""
    id: str
    messages: List[Message]
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    """Model representing a response from an agent."""
    agent_id: str
    agent_name: str
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    thinking: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)

class FunctionCall(BaseModel):
    """Model representing a function call."""
    name: str
    arguments: Dict[str, Any]
    description: Optional[str] = None

class FunctionResult(BaseModel):
    """Model representing a function result."""
    name: str
    result: Any
    error: Optional[str] = None
    execution_time: Optional[float] = None

class TaskStatus(str, Enum):
    """Status of an asynchronous task."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task(BaseModel):
    """Model representing an asynchronous task."""
    id: str
    status: TaskStatus
    progress: float = Field(0.0, ge=0.0, le=1.0)
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True
