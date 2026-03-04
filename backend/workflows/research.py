"""
Research Workflow - For searching and summarizing information.
"""

from typing import List
from backend.models.schemas import WorkflowType, Skill, Plan
from backend.workflows.base import BaseWorkflow


class ResearchWorkflow(BaseWorkflow):
    """Workflow for research and information gathering tasks."""

    def __init__(self):
        super().__init__(WorkflowType.RESEARCH)

    async def execute(
        self,
        user_message: str,
        plan: Plan,
        tool_executor,
        model=None
    ) -> str:
        """Execute the research workflow."""
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
                        f"Based on the user's research request: '{user_message}', "
                        f"provide a comprehensive response for step {step.step_number}. "
                        f"Step description: {step.description}"
                    )
                    step.tool_output = response.text
                    step.status = "completed"
                    results.append(f"Step {step.step_number}: {response.text}")
                else:
                    step.status = "completed"
                    results.append(f"Step {step.step_number}: Research complete")

        return "\n\n".join(results)

    def get_available_tools(self) -> List[Skill]:
        """Get tools available for research."""
        return [
            Skill(
                tool_name="web_search",
                description="Search the web for information",
                arguments=[
                    {"name": "query", "type": "string", "description": "Search query"},
                    {"name": "num_results", "type": "integer", "description": "Number of results"}
                ],
                execution_code="",
                category="search"
            ),
            Skill(
                tool_name="content_summarizer",
                description="Summarize long content into concise summaries",
                arguments=[
                    {"name": "content", "type": "string", "description": "Content to summarize"},
                    {"name": "max_length", "type": "integer", "description": "Max summary length"}
                ],
                execution_code="",
                category="research"
            ),
            Skill(
                tool_name="citation_generator",
                description="Generate citations for sources",
                arguments=[
                    {"name": "source", "type": "string", "description": "Source URL or title"},
                    {"name": "style", "type": "string", "description": "Citation style (APA, MLA, etc.)"}
                ],
                execution_code="",
                category="research"
            )
        ]
