"""
Workflows package - Contains workflow implementations for different task types.
"""

from .base import BaseWorkflow, WorkflowRegistry, get_workflow_registry
from .data_analysis import DataAnalysisWorkflow
from .code_gen import CodeGenWorkflow
from .research import ResearchWorkflow
from .general_chat import GeneralChatWorkflow


def register_all_workflows():
    """Register all workflow implementations."""
    registry = get_workflow_registry()

    # Register all workflows
    registry.register(DataAnalysisWorkflow())
    registry.register(CodeGenWorkflow())
    registry.register(ResearchWorkflow())
    registry.register(GeneralChatWorkflow())


__all__ = [
    "BaseWorkflow",
    "WorkflowRegistry",
    "get_workflow_registry",
    "DataAnalysisWorkflow",
    "CodeGenWorkflow",
    "ResearchWorkflow",
    "GeneralChatWorkflow",
    "register_all_workflows"
]
