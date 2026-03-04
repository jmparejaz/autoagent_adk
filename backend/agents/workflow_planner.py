"""
Workflow Planner - Decomposes tasks into steps with reasoning.
"""

import json
from typing import List, Optional, Dict, Any
from backend.models.schemas import (
    IntentClassification,
    ReasoningStep,
    Plan,
    WorkflowType,
    Skill
)


class WorkflowPlanner:
    """Plans and decomposes tasks into executable steps."""

    def __init__(self, model=None, skill_loader=None):
        """Initialize the workflow planner."""
        self.model = model
        self.skill_loader = skill_loader

    async def create_plan(
        self,
        user_message: str,
        intent: IntentClassification,
        available_tools: List[Skill]
    ) -> Plan:
        """
        Create an execution plan for the given intent.

        Args:
            user_message: The user's input message
            intent: The classified intent
            available_tools: List of available tools/skills

        Returns:
            Plan with reasoning steps
        """
        if self.model:
            return await self._create_llm_plan(user_message, intent, available_tools)
        else:
            return self._create_rule_based_plan(user_message, intent, available_tools)

    async def _create_llm_plan(
        self,
        user_message: str,
        intent: IntentClassification,
        available_tools: List[Skill]
    ) -> Plan:
        """Use LLM to create a detailed plan."""
        tools_description = "\n".join([
            f"- {t.tool_name}: {t.description}"
            for t in available_tools
        ])

        prompt = f"""You are a task planner for an AI agent system.

Given the user's message and intent, break down the task into clear steps.

User message: {user_message}
Intent: {intent.workflow.value}
Confidence: {intent.confidence}

Available tools:
{tools_description}

Create a plan with numbered steps. For each step, indicate:
1. What needs to be done
2. Which tool to use (if any)
3. What the input and expected output should be

Return your plan in JSON format:
{{
    "goal": "The main goal to achieve",
    "steps": [
        {{
            "step_number": 1,
            "description": "What this step does",
            "tool_used": "tool_name or null",
            "tool_input": {{}} or null
        }}
    ]
}}

Only return valid JSON."""

        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)

            steps = []
            for step_data in result.get("steps", []):
                step = ReasoningStep(
                    step_number=step_data.get("step_number", 1),
                    description=step_data.get("description", ""),
                    tool_used=step_data.get("tool_used"),
                    tool_input=step_data.get("tool_input"),
                    status="pending"
                )
                steps.append(step)

            return Plan(
                goal=result.get("goal", user_message),
                steps=steps,
                current_step=0,
                is_complete=False
            )
        except Exception as e:
            print(f"Error in LLM planning: {e}")
            return self._create_rule_based_plan(user_message, intent, available_tools)

    def _create_rule_based_plan(
        self,
        user_message: str,
        intent: IntentClassification,
        available_tools: List[Skill]
    ) -> Plan:
        """Create a plan using rules."""
        steps = []

        # Get tools for this workflow type
        workflow_tools = self._get_workflow_tools(intent.workflow, available_tools)

        if not workflow_tools:
            # No specific tools, just one step for conversation
            steps.append(ReasoningStep(
                step_number=1,
                description="Process the user's request with the language model",
                tool_used=None,
                status="pending"
            ))
        else:
            # Create steps based on workflow
            for i, tool in enumerate(workflow_tools, 1):
                steps.append(ReasoningStep(
                    step_number=i,
                    description=f"Execute {tool.tool_name}: {tool.description}",
                    tool_used=tool.tool_name,
                    tool_input={"query": user_message},
                    status="pending"
                ))

        return Plan(
            goal=user_message,
            steps=steps,
            current_step=0,
            is_complete=False
        )

    def _get_workflow_tools(
        self,
        workflow: WorkflowType,
        available_tools: List[Skill]
    ) -> List[Skill]:
        """Get relevant tools for a workflow."""
        # Map workflows to tool categories
        workflow_categories = {
            WorkflowType.DATA_ANALYSIS: ["data", "analysis", "chart"],
            WorkflowType.CODE_GEN: ["code", "developer"],
            WorkflowType.RESEARCH: ["search", "research", "web"],
            WorkflowType.GENERAL_CHAT: []
        }

        categories = workflow_categories.get(workflow, [])

        if not categories:
            return []

        return [
            tool for tool in available_tools
            if any(cat in tool.category.lower() for cat in categories)
        ]

    async def update_step_status(
        self,
        plan: Plan,
        step_number: int,
        status: str,
        tool_output: Any = None
    ) -> Plan:
        """Update the status of a step in the plan."""
        if 0 <= step_number < len(plan.steps):
            plan.steps[step_number].status = status
            if tool_output is not None:
                plan.steps[step_number].tool_output = tool_output

            # Check if plan is complete
            if all(step.status == "completed" for step in plan.steps):
                plan.is_complete = True

        return plan


# Global planner instance
_planner: Optional[WorkflowPlanner] = None


def get_workflow_planner(model=None, skill_loader=None) -> WorkflowPlanner:
    """Get the global workflow planner instance."""
    global _planner
    if _planner is None:
        _planner = WorkflowPlanner(model, skill_loader)
    return _planner
