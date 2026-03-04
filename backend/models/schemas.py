"""
Data models and schemas for the agentic platform.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class WorkflowType(str, Enum):
    """Available workflow types."""
    DATA_ANALYSIS = "data_analysis"
    CODE_GEN = "code_gen"
    RESEARCH = "research"
    GENERAL_CHAT = "general_chat"


class IntentClassification(BaseModel):
    """Intent classification result."""
    workflow: WorkflowType
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    suggested_tools: List[str] = []


class ReasoningStep(BaseModel):
    """A single reasoning step in the planning process."""
    step_number: int
    description: str
    tool_used: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Any] = None
    status: str = "pending"  # pending, in_progress, completed, failed


class Plan(BaseModel):
    """Execution plan with reasoning steps."""
    goal: str
    steps: List[ReasoningStep] = []
    current_step: int = 0
    is_complete: bool = False


class Skill(BaseModel):
    """A skill/tool definition loaded from markdown."""
    tool_name: str
    description: str
    arguments: List[Dict[str, str]] = []
    execution_code: str
    category: str = "general"


class Message(BaseModel):
    """Chat message."""
    id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    reasoning_steps: List[ReasoningStep] = []
    tools_used: List[str] = []


class Session(BaseModel):
    """Chat session."""
    id: str
    workflow: Optional[WorkflowType] = None
    messages: List[Message] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Chat request payload."""
    message: str
    session_id: Optional[str] = None
    workflow_override: Optional[WorkflowType] = None


class ChatResponse(BaseModel):
    """Chat response payload."""
    message: Message
    intent: IntentClassification
    plan: Plan
    session_id: str


class ToolCallRequest(BaseModel):
    """Request to execute a specific tool."""
    tool_name: str
    arguments: Dict[str, Any]


class ToolCallResponse(BaseModel):
    """Response from tool execution."""
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
