"""
Base workflow class and registry.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from backend.models.schemas import WorkflowType, Skill, Plan


class BaseWorkflow(ABC):
    """Base class for all workflows."""

    def __init__(self, workflow_type: WorkflowType):
        self.workflow_type = workflow_type

    @abstractmethod
    async def execute(
        self,
        user_message: str,
        plan: Plan,
        tool_executor,
        model=None
    ) -> str:
        """Execute the workflow."""
        pass

    @abstractmethod
    def get_available_tools(self) -> List[Skill]:
        """Get tools available for this workflow."""
        pass


class WorkflowRegistry:
    """Registry for all available workflows."""

    def __init__(self):
        self._workflows: Dict[WorkflowType, BaseWorkflow] = {}

    def register(self, workflow: BaseWorkflow):
        """Register a workflow."""
        self._workflows[workflow.workflow_type] = workflow

    def get_workflow(self, workflow_type: WorkflowType) -> Optional[BaseWorkflow]:
        """Get a workflow by type."""
        return self._workflows.get(workflow_type)

    def get_all_workflows(self) -> Dict[WorkflowType, BaseWorkflow]:
        """Get all registered workflows."""
        return self._workflows


# Global registry
_registry: Optional[WorkflowRegistry] = None


def get_workflow_registry() -> WorkflowRegistry:
    """Get the global workflow registry."""
    global _registry
    if _registry is None:
        _registry = WorkflowRegistry()
    return _registry
