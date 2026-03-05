"""
ADK Agents Package — Google ADK + Gemini 2.5 Flash agent implementations.

All agents are backed by the official `google-adk` library.
The legacy hand-rolled classes (IntentClassifier, WorkflowPlanner, ToolExecutor)
have been removed; use the ADK-native equivalents below.

Install dependency:
    pip install google-adk
"""

from .adk_agents import (
    # Config / base
    ADKAgentConfig,
    ADKAgentBase,
    # Core agents
    IntentClassifierAgent,
    WorkflowPlannerAgent,
    ToolExecutorAgent,
    # Orchestration agents
    SequentialWorkflowAgent,
    ParallelWorkflowAgent,
    LoopWorkflowAgent,
    # Singleton accessors
    get_intent_classifier,
    get_workflow_planner,
    get_tool_executor,
    # Built-in FunctionTools (useful for extending skill sets)
    BUILTIN_TOOLS,
)

__all__ = [
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
    "BUILTIN_TOOLS",
]
