"""
ADK Agents Package - Google ADK-based agent implementations.
"""

# Import ADK-based agents
from .adk_agents import (
    ADKAgentConfig,
    ADKAgentBase,
    IntentClassifierAgent,
    WorkflowPlannerAgent,
    ToolExecutorAgent,
    SequentialWorkflowAgent,
    ParallelWorkflowAgent,
    LoopWorkflowAgent,
    get_intent_classifier,
    get_workflow_planner,
    get_tool_executor
)

# Legacy imports for backwards compatibility
from .intent_classifier import IntentClassifier, get_intent_classifier as get_legacy_intent_classifier
from .workflow_planner import WorkflowPlanner, get_workflow_planner as get_legacy_workflow_planner
from .tool_executor import ToolExecutor, get_tool_executor as get_legacy_tool_executor

__all__ = [
    # ADK Agents
    "ADKAgentConfig",
    "ADKAgentBase",
    "IntentClassifierAgent",
    "WorkflowPlannerAgent",
    "ToolExecutorAgent",
    "SequentialWorkflowAgent",
    "ParallelWorkflowAgent",
    "LoopWorkflowAgent",
    "get_intent_classifier",
    "get_workflow_planner",
    "get_tool_executor",
    # Legacy Agents
    "IntentClassifier",
    "WorkflowPlanner",
    "ToolExecutor",
    "get_legacy_intent_classifier",
    "get_legacy_workflow_planner",
    "get_legacy_tool_executor"
]
