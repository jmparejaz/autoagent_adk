"""
Tool Executor - Executes tools decided by the workflow planner.
"""

import asyncio
import json
from typing import Any, Dict, Optional
from backend.models.schemas import Skill, ToolCallResponse


class ToolExecutor:
    """Executes tools/skills defined in the system."""

    def __init__(self, skill_loader=None):
        """Initialize the tool executor."""
        self.skill_loader = skill_loader
        self._tool_registry: Dict[str, callable] = {}
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """Register built-in tools that don't come from markdown files."""
        # Register built-in tools here
        self._tool_registry["echo"] = self._echo_tool
        self._tool_registry["get_date"] = self._get_date_tool
        self._tool_registry["calculate"] = self._calculate_tool

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> ToolCallResponse:
        """
        Execute a tool by name with given arguments.

        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool

        Returns:
            ToolCallResponse with result or error
        """
        # First check built-in tools
        if tool_name in self._tool_registry:
            try:
                result = await self._tool_registry[tool_name](arguments)
                return ToolCallResponse(
                    tool_name=tool_name,
                    success=True,
                    result=result
                )
            except Exception as e:
                return ToolCallResponse(
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=str(e)
                )

        # Then check skill loader
        if self.skill_loader:
            skill = self.skill_loader.get_skill(tool_name)
            if skill:
                try:
                    result = await self._execute_skill(skill, arguments)
                    return ToolCallResponse(
                        tool_name=tool_name,
                        success=True,
                        result=result
                    )
                except Exception as e:
                    return ToolCallResponse(
                        tool_name=tool_name,
                        success=False,
                        result=None,
                        error=str(e)
                    )

        # Tool not found
        return ToolCallResponse(
            tool_name=tool_name,
            success=False,
            result=None,
            error=f"Tool '{tool_name}' not found"
        )

    async def _execute_skill(
        self,
        skill: Skill,
        arguments: Dict[str, Any]
    ) -> Any:
        """Execute a skill from the skill loader."""
        # For now, we'll simulate skill execution
        # In a real implementation, this would dynamically execute code
        # defined in the markdown file

        # Simulate some processing time
        await asyncio.sleep(0.1)

        # Return a mock result based on the skill
        return {
            "skill": skill.tool_name,
            "description": skill.description,
            "input": arguments,
            "output": f"Executed {skill.tool_name} successfully"
        }

    # Built-in tool implementations
    async def _echo_tool(self, arguments: Dict[str, Any]) -> str:
        """Echo back the input."""
        return arguments.get("message", "No message provided")

    async def _get_date_tool(self, arguments: Dict[str, Any]) -> str:
        """Get the current date."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    async def _calculate_tool(self, arguments: Dict[str, Any]) -> float:
        """Perform a calculation."""
        expression = arguments.get("expression", "0")
        try:
            # WARNING: eval is dangerous in production!
            # Use a proper math parser in production
            result = eval(expression, {"__builtins__": {}}, {})
            return result
        except Exception as e:
            raise ValueError(f"Calculation error: {e}")

    def register_custom_tool(self, name: str, func: callable):
        """Register a custom tool function."""
        self._tool_registry[name] = func

    def get_available_tools(self) -> list:
        """Get list of all available tool names."""
        tools = list(self._tool_registry.keys())

        if self.skill_loader:
            skills = self.skill_loader.get_all_skills()
            tools.extend(skills.keys())

        return tools


# Global executor instance
_executor: Optional[ToolExecutor] = None


def get_tool_executor(skill_loader=None) -> ToolExecutor:
    """Get the global tool executor instance."""
    global _executor
    if _executor is None:
        _executor = ToolExecutor(skill_loader)
    return _executor
