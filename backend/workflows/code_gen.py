"""
Code Generation Workflow - For writing, reviewing, and debugging code.
"""

from typing import List
from backend.models.schemas import WorkflowType, Skill, Plan
from backend.workflows.base import BaseWorkflow


class CodeGenWorkflow(BaseWorkflow):
    """Workflow for code generation tasks."""

    def __init__(self):
        super().__init__(WorkflowType.CODE_GEN)

    async def execute(
        self,
        user_message: str,
        plan: Plan,
        tool_executor,
        model=None
    ) -> str:
        """Execute the code generation workflow."""
        results = []

        for step in plan.steps:
            if step.tool_used:
                # Execute the tool
                tool_args = step.tool_input or {"code": user_message}
                response = await tool_executor.execute_tool(
                    step.tool_used,
                    tool_args
                )

                if response.success:
                    results.append(f"Step {step.step_number}: {response.result}")
                    step.tool_output = response.result
                    step.status = "completed"
                else:
                    results.append(f"Step {step.step_number} failed: {response.error}")
                    step.status = "failed"
                    break
            else:
                # Use LLM for non-tool steps
                if model:
                    step.status = "in_progress"
                    response = model.generate_content(
                        f"Based on the user's request: '{user_message}', "
                        f"provide a code-related response for step {step.step_number}. "
                        f"Step description: {step.description}"
                    )
                    step.tool_output = response.text
                    step.status = "completed"
                    results.append(f"Step {step.step_number}: {response.text}")
                else:
                    step.status = "completed"
                    results.append(f"Step {step.step_number}: Code generation complete")

        return "\n\n".join(results)

    def get_available_tools(self) -> List[Skill]:
        """Get tools available for code generation."""
        return [
            Skill(
                tool_name="code_writer",
                description="Write code in various programming languages",
                arguments=[
                    {"name": "language", "type": "string", "description": "Programming language"},
                    {"name": "task", "type": "string", "description": "Code to write"}
                ],
                execution_code="",
                category="code"
            ),
            Skill(
                tool_name="code_reviewer",
                description="Review code for bugs, style issues, and improvements",
                arguments=[
                    {"name": "code", "type": "string", "description": "Code to review"}
                ],
                execution_code="",
                category="developer"
            ),
            Skill(
                tool_name="bug_detector",
                description="Detect bugs and issues in code",
                arguments=[
                    {"name": "code", "type": "string", "description": "Code to analyze"}
                ],
                execution_code="",
                category="developer"
            ),
            Skill(
                tool_name="code_explainer",
                description="Explain what code does in plain language",
                arguments=[
                    {"name": "code", "type": "string", "description": "Code to explain"}
                ],
                execution_code="",
                category="developer"
            )
        ]
