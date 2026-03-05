"""
Base workflow class and registry.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from backend.models.schemas import WorkflowType, Skill, Plan, Workflow
from backend.agents.adk_adapter import workflow_to_adk_tool, FunctionTool


class BaseWorkflow(ABC):
    """Base class for all workflows."""

    def __init__(self, workflow_type: WorkflowType, name: Optional[str] = None, description: Optional[str] = None):
        self.workflow_type = workflow_type
        self.name = name or workflow_type.value.replace("_", " ").title()
        self.description = description or f"Workflow for {self.name} tasks"

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

    def to_schema(self) -> Workflow:
        """Convert the workflow implementation to a Workflow schema."""
        return Workflow(
            name=self.name,
            description=self.description,
            steps=[{
                "name": "execute_workflow",
                "type": "workflow_execution",
                "description": f"Main execution step for {self.name}"
            }],
            inputs=[{"name": "user_message", "type": "str", "description": "The user input"}]
        )


class WorkflowRegistry:
    """Registry for all available workflows."""

    def __init__(self):
        self._workflows: Dict[WorkflowType, BaseWorkflow] = {}
        self._adk_tools: Dict[WorkflowType, FunctionTool] = {}

    def register(self, workflow: BaseWorkflow):
        """Register a workflow and convert it to an ADK tool."""
        self._workflows[workflow.workflow_type] = workflow
        
        # Convert workflow to ADK tool
        try:
            workflow_schema = workflow.to_schema()
            adk_tool = workflow_to_adk_tool(workflow_schema)
            self._adk_tools[workflow.workflow_type] = adk_tool
        except Exception as e:
            print(f"Warning: Could not convert workflow '{workflow.name}' to ADK tool: {e}")

    def get_workflow(self, workflow_type: WorkflowType) -> Optional[BaseWorkflow]:
        """Get a workflow by type."""
        return self._workflows.get(workflow_type)

    def get_all_workflows(self) -> Dict[WorkflowType, BaseWorkflow]:
        """Get all registered workflows."""
        return self._workflows
    
    def get_adk_tools(self) -> List[FunctionTool]:
        """Get all workflows as ADK FunctionTools."""
        return list(self._adk_tools.values())


# Global registry
_registry: Optional[WorkflowRegistry] = None


def get_workflow_registry() -> WorkflowRegistry:
    """Get the global workflow registry."""
    global _registry
    if _registry is None:
        _registry = WorkflowRegistry()
    return _registry
