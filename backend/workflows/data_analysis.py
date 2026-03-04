"""
Data Analysis Workflow - For analyzing data and generating insights.
"""

from typing import List
from backend.models.schemas import WorkflowType, Skill, Plan
from backend.workflows.base import BaseWorkflow


class DataAnalysisWorkflow(BaseWorkflow):
    """Workflow for data analysis tasks."""

    def __init__(self):
        super().__init__(WorkflowType.DATA_ANALYSIS)

    async def execute(
        self,
        user_message: str,
        plan: Plan,
        tool_executor,
        model=None
    ) -> str:
        """Execute the data analysis workflow."""
        results = []

        for step in plan.steps:
            if step.tool_used:
                # Execute the tool
                tool_args = step.tool_input or {"query": user_message}
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
                        f"provide a data analysis response for step {step.step_number}. "
                        f"Step description: {step.description}"
                    )
                    step.tool_output = response.text
                    step.status = "completed"
                    results.append(f"Step {step.step_number}: {response.text}")
                else:
                    step.status = "completed"
                    results.append(f"Step {step.step_number}: Analysis complete")

        return "\n\n".join(results)

    def get_available_tools(self) -> List[Skill]:
        """Get tools available for data analysis."""
        return [
            Skill(
                tool_name="data_query",
                description="Query and analyze data from databases or files",
                arguments=[
                    {"name": "query", "type": "string", "description": "The data query"}
                ],
                execution_code="",
                category="data"
            ),
            Skill(
                tool_name="chart_generator",
                description="Generate charts and visualizations from data",
                arguments=[
                    {"name": "data", "type": "object", "description": "Data to visualize"},
                    {"name": "chart_type", "type": "string", "description": "Type of chart"}
                ],
                execution_code="",
                category="analysis"
            ),
            Skill(
                tool_name="report_builder",
                description="Build formatted reports from analysis results",
                arguments=[
                    {"name": "title", "type": "string", "description": "Report title"},
                    {"name": "content", "type": "string", "description": "Report content"}
                ],
                execution_code="",
                category="analysis"
            )
        ]
