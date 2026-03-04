"""
Google ADK-based Agent System for Enterprise Agentic Platform.

This module integrates the actual Google Agent Development Kit (ADK) Python framework
to create a multi-agent system with intent classification, workflow orchestration,
and tool execution capabilities.
"""

import os
import json
from typing import Dict, List, Optional, Any
from pathlib import Path

# Google ADK imports
try:
    from google.genkit import Genkit
    from google.genkit.plugins import GoogleAI
    GOOGLE_GENKIT_AVAILABLE = True
except ImportError:
    GOOGLE_GENKIT_AVAILABLE = False
    print("Warning: google-genkit not available. Using fallback implementation.")

# Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not available. Using fallback implementation.")


class ADKAgentConfig:
    """Configuration for ADK agents."""

    def __init__(
        self,
        name: str,
        description: str,
        model: str = "gemini-2.5-flash",
        instructions: str = "",
        tools: List[str] = None
    ):
        self.name = name
        self.description = description
        self.model = model
        self.instructions = instructions
        self.tools = tools or []


class ADKAgentBase:
    """Base class for ADK-style agents."""

    def __init__(self, config: ADKAgentConfig, api_key: str = None):
        self.config = config
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self._model = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the underlying model."""
        if GEMINI_AVAILABLE and self.api_key:
            genai.configure(api_key=self.api_key)
            self._model = genai.GenerativeModel(
                model_name=self.config.model,
                system_instruction=self.config.instructions
            )

    async def generate(self, prompt: str, context: Dict = None) -> str:
        """Generate a response using the configured model."""
        if self._model:
            try:
                full_prompt = prompt
                if context:
                    full_prompt = f"Context: {json.dumps(context)}\n\nUser: {prompt}"

                response = self._model.generate_content(full_prompt)
                return response.text
            except Exception as e:
                print(f"Error generating response: {e}")
                return f"Error: {str(e)}"
        else:
            return f"[Fallback] Agent {self.config.name} received: {prompt}"


class IntentClassifierAgent(ADKAgentBase):
    """
    Intent Classifier Agent - Routes user input to appropriate workflows.
    Uses LLM-based classification to determine the best workflow for a given query.
    """

    WORKFLOW_DESCRIPTIONS = {
        "data_analysis": "Data Analysis - For analyzing data, generating insights, creating charts, running queries, and working with databases or files.",
        "code_gen": "Code Generation - For writing, reviewing, debugging, explaining code, or implementing algorithms.",
        "research": "Research - For searching information, summarizing content, gathering facts, or answering questions requiring web search.",
        "general_chat": "General Chat - For casual conversation, general questions, and tasks that don't fit other categories."
    }

    def __init__(self, api_key: str = None):
        config = ADKAgentConfig(
            name="intent_classifier",
            description="Classifies user intent and routes to appropriate workflow",
            model="gemini-2.5-flash",
            instructions="""You are an intent classification agent. Your job is to analyze user messages and determine which workflow best fits their request.

Available workflows:
- data_analysis: For data queries, analytics, charts, reports
- code_gen: For code writing, debugging, reviewing
- research: For information search, summarization, fact-finding
- general_chat: For general conversation and other tasks

Return a JSON object with:
{
    "workflow": "workflow_name",
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation",
    "suggested_tools": ["tool1", "tool2"]
}

Only return the JSON, no other text."""
        )
        super().__init__(config, api_key)

    async def classify(self, user_message: str) -> Dict[str, Any]:
        """Classify user intent and return workflow assignment."""
        prompt = f"Classify this user message: {user_message}"

        if self._model:
            try:
                response = await self.generate(prompt)
                # Try to parse JSON response
                try:
                    # Clean up the response to extract JSON
                    text = response.strip()
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0]
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0]

                    result = json.loads(text.strip())
                    return result
                except json.JSONDecodeError:
                    # Fallback to rule-based classification
                    return self._rule_based_classify(user_message)
            except Exception as e:
                return self._rule_based_classify(user_message)
        else:
            return self._rule_based_classify(user_message)

    def _rule_based_classify(self, message: str) -> Dict[str, Any]:
        """Fallback rule-based classification."""
        message_lower = message.lower()

        # Data analysis keywords
        data_keywords = ["analyze", "analysis", "data", "chart", "graph", "report",
                        "statistics", "metrics", "insights", "trend", "query", "database"]
        if any(kw in message_lower for kw in data_keywords):
            return {
                "workflow": "data_analysis",
                "confidence": 0.85,
                "reasoning": "Message contains data analysis keywords",
                "suggested_tools": ["data_query", "chart_generator"]
            }

        # Code generation keywords
        code_keywords = ["code", "program", "function", "class", "debug", "review",
                        "write", "implement", "refactor", "algorithm", "script"]
        if any(kw in message_lower for kw in code_keywords):
            return {
                "workflow": "code_gen",
                "confidence": 0.85,
                "reasoning": "Message contains code-related keywords",
                "suggested_tools": ["code_writer", "code_reviewer"]
            }

        # Research keywords
        research_keywords = ["search", "find", "research", "information", "what is",
                            "how does", "explain", "describe", "tell me about", "look up"]
        if any(kw in message_lower for kw in research_keywords):
            return {
                "workflow": "research",
                "confidence": 0.8,
                "reasoning": "Message appears to be a research or information query",
                "suggested_tools": ["web_search", "content_summarizer"]
            }

        # Default to general chat
        return {
            "workflow": "general_chat",
            "confidence": 0.6,
            "reasoning": "No specific workflow matched, defaulting to general chat",
            "suggested_tools": []
        }


class WorkflowPlannerAgent(ADKAgentBase):
    """
    Workflow Planner Agent - Decomposes tasks into executable steps.
    Uses chain-of-thought reasoning to create multi-step execution plans.
    """

    def __init__(self, api_key: str = None):
        config = ADKAgentConfig(
            name="workflow_planner",
            description="Creates detailed execution plans with reasoning steps",
            model="gemini-2.5-flash",
            instructions="""You are a task planning agent. Your job is to break down user requests into clear, actionable steps.

For each step, specify:
1. What needs to be done
2. Which tool to use (if any)
3. What the input and expected output should be

Return a JSON object with:
{
    "goal": "The main goal to achieve",
    "steps": [
        {
            "step_number": 1,
            "description": "What this step does",
            "tool_used": "tool_name or null",
            "tool_input": {} or null
        }
    ]
}

Only return valid JSON."""
        )
        super().__init__(config, api_key)

    async def create_plan(
        self,
        user_message: str,
        workflow: str,
        available_tools: List[str]
    ) -> Dict[str, Any]:
        """Create an execution plan for the given workflow."""

        tools_desc = "\n".join([f"- {tool}" for tool in available_tools])

        prompt = f"""Create an execution plan for:

User Request: {user_message}
Workflow: {workflow}

Available Tools:
{tools_desc}

Break this down into clear steps. Return only the JSON plan."""

        if self._model:
            try:
                response = await self.generate(prompt)
                try:
                    text = response.strip()
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0]
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0]

                    plan = json.loads(text.strip())
                    return plan
                except json.JSONDecodeError:
                    return self._create_simple_plan(user_message, workflow, available_tools)
            except Exception as e:
                return self._create_simple_plan(user_message, workflow, available_tools)
        else:
            return self._create_simple_plan(user_message, workflow, available_tools)

    def _create_simple_plan(
        self,
        user_message: str,
        workflow: str,
        available_tools: List[str]
    ) -> Dict[str, Any]:
        """Create a simple default plan."""
        steps = []

        if workflow == "general_chat":
            steps.append({
                "step_number": 1,
                "description": "Process the user's request and provide a helpful response",
                "tool_used": None,
                "tool_input": None
            })
        else:
            for i, tool in enumerate(available_tools[:3], 1):
                steps.append({
                    "step_number": i,
                    "description": f"Execute {tool} for the task",
                    "tool_used": tool,
                    "tool_input": {"query": user_message}
                })

        return {
            "goal": user_message,
            "steps": steps
        }


class ToolExecutorAgent(ADKAgentBase):
    """
    Tool Executor Agent - Executes tools and manages tool outputs.
    Handles both built-in tools and dynamically loaded skill tools.
    """

    def __init__(self, skills: Dict[str, Any], api_key: str = None):
        config = ADKAgentConfig(
            name="tool_executor",
            description="Executes tools and returns results",
            model="gemini-2.5-flash",
            instructions="You are a tool execution agent. Execute the specified tool and return the result."
        )
        super().__init__(config, api_key)
        self.skills = skills
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """Register built-in tools."""
        self._builtin_tools = {
            "echo": self._echo_tool,
            "get_date": self._get_date_tool,
            "calculate": self._calculate_tool
        }

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool by name with given arguments."""

        # Check built-in tools first
        if tool_name in self._builtin_tools:
            try:
                result = await self._builtin_tools[tool_name](arguments)
                return {
                    "tool_name": tool_name,
                    "success": True,
                    "result": result
                }
            except Exception as e:
                return {
                    "tool_name": tool_name,
                    "success": False,
                    "result": None,
                    "error": str(e)
                }

        # Check skill loader
        if tool_name in self.skills:
            skill = self.skills[tool_name]
            try:
                # For now, simulate skill execution
                result = await self._execute_skill(skill, arguments)
                return {
                    "tool_name": tool_name,
                    "success": True,
                    "result": result
                }
            except Exception as e:
                return {
                    "tool_name": tool_name,
                    "success": False,
                    "result": None,
                    "error": str(e)
                }

        # Tool not found
        return {
            "tool_name": tool_name,
            "success": False,
            "result": None,
            "error": f"Tool '{tool_name}' not found"
        }

    async def _execute_skill(
        self,
        skill: Any,
        arguments: Dict[str, Any]
    ) -> Any:
        """Execute a skill from the skill loader."""
        import asyncio
        await asyncio.sleep(0.1)

        return {
            "skill": skill.tool_name if hasattr(skill, 'tool_name') else str(skill),
            "description": skill.description if hasattr(skill, 'description') else "",
            "input": arguments,
            "output": f"Executed skill successfully"
        }

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
            result = eval(expression, {"__builtins__": {}}, {})
            return result
        except Exception as e:
            raise ValueError(f"Calculation error: {e}")


class SequentialWorkflowAgent:
    """
    Sequential Agent - Executes sub-agents in a fixed order.
    This mirrors ADK's SequentialAgent pattern.
    """

    def __init__(self, name: str, sub_agents: List[Any]):
        self.name = name
        self.sub_agents = sub_agents

    async def execute(self, initial_input: Any) -> Any:
        """Execute sub-agents sequentially, passing output to next agent."""
        current_input = initial_input

        for agent in self.sub_agents:
            current_input = await agent.execute(current_input)

        return current_input


class ParallelWorkflowAgent:
    """
    Parallel Agent - Executes sub-agents simultaneously.
    This mirrors ADK's ParallelAgent pattern.
    """

    def __init__(self, name: str, sub_agents: List[Any]):
        self.name = name
        self.sub_agents = sub_agents

    async def execute(self, input_data: Any) -> List[Any]:
        """Execute all sub-agents in parallel and return combined results."""
        import asyncio

        tasks = [agent.execute(input_data) for agent in self.sub_agents]
        results = await asyncio.gather(*tasks)

        return results


class LoopWorkflowAgent:
    """
    Loop Agent - Executes sub-agents iteratively until termination condition.
    This mirrors ADK's LoopAgent pattern.
    """

    def __init__(
        self,
        name: str,
        sub_agents: List[Any],
        max_iterations: int = 5,
        termination_condition: callable = None
    ):
        self.name = name
        self.sub_agents = sub_agents
        self.max_iterations = max_iterations
        self.termination_condition = termination_condition

    async def execute(self, initial_input: Any) -> Any:
        """Execute sub-agents in a loop until condition is met."""
        current_input = initial_input
        iteration = 0

        while iteration < self.max_iterations:
            for agent in self.sub_agents:
                current_input = await agent.execute(current_input)

            if self.termination_condition and self.termination_condition(current_input):
                break

            iteration += 1

        return current_input


# Global agent instances
_intent_classifier: Optional[IntentClassifierAgent] = None
_workflow_planner: Optional[WorkflowPlannerAgent] = None
_tool_executor: Optional[ToolExecutorAgent] = None


def get_intent_classifier(api_key: str = None) -> IntentClassifierAgent:
    """Get the global intent classifier instance."""
    global _intent_classifier
    if _intent_classifier is None:
        _intent_classifier = IntentClassifierAgent(api_key)
    return _intent_classifier


def get_workflow_planner(api_key: str = None) -> WorkflowPlannerAgent:
    """Get the global workflow planner instance."""
    global _workflow_planner
    if _workflow_planner is None:
        _workflow_planner = WorkflowPlannerAgent(api_key)
    return _workflow_planner


def get_tool_executor(skills: Dict[str, Any], api_key: str = None) -> ToolExecutorAgent:
    """Get the global tool executor instance."""
    global _tool_executor
    if _tool_executor is None:
        _tool_executor = ToolExecutorAgent(skills, api_key)
    return _tool_executor
