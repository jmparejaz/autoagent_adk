"""
General Chat Workflow - For casual conversation and general assistance.
"""

from typing import List
from backend.models.schemas import WorkflowType, Skill, Plan
from backend.workflows.base import BaseWorkflow


class GeneralChatWorkflow(BaseWorkflow):
    """Workflow for general conversation and assistance."""

    def __init__(self):
        super().__init__(WorkflowType.GENERAL_CHAT)

    async def execute(
        self,
        user_message: str,
        plan: Plan,
        tool_executor,
        model=None
    ) -> str:
        """Execute the general chat workflow."""
        # For general chat, we primarily use the LLM
        if model:
            # Mark first step as in progress
            if plan.steps:
                plan.steps[0].status = "in_progress"

            # Generate response using the model
            response = model.generate_content(
                f"You are a helpful AI assistant. Respond to the following user message: {user_message}"
            )

            # Update step status
            if plan.steps:
                plan.steps[0].tool_output = response.text
                plan.steps[0].status = "completed"

            return response.text
        else:
            # Fallback if no model is available
            if plan.steps:
                plan.steps[0].status = "completed"
            return "Hello! I'm your AI assistant. How can I help you today?"

    def get_available_tools(self) -> List[Skill]:
        """Get tools available for general chat."""
        # General chat has minimal tools - mostly conversational
        return [
            Skill(
                tool_name="weather查询",
                description="Get current weather information",
                arguments=[
                    {"name": "location", "type": "string", "description": "Location to check weather"}
                ],
                execution_code="",
                category="general"
            ),
            Skill(
                tool_name="calculator",
                description="Perform mathematical calculations",
                arguments=[
                    {"name": "expression", "type": "string", "description": "Math expression"}
                ],
                execution_code="",
                category="general"
            )
        ]
