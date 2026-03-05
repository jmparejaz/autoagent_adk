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
from datetime import datetime

# Google ADK imports
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types


# ---------------------------------------------------------------------------
# Model helper
# ---------------------------------------------------------------------------

def _make_model(api_key: str | None = None) -> LiteLlm:
    """Return a LiteLlm wrapper for Gemini 2.5 Flash via the Gemini API."""
    key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise ValueError(
            "A Gemini API key is required. Pass api_key= or set GEMINI_API_KEY."
        )
    # LiteLlm uses the litellm routing string; gemini/ prefix → Gemini API
    return LiteLlm(
        model="gemini/gemini-2.5-flash",
        api_key=key,
    )


# ---------------------------------------------------------------------------
# Built-in FunctionTools
# ---------------------------------------------------------------------------

def echo(message: str) -> str:
    """Echo a message back to the caller.

    Args:
        message: The text to echo.

    Returns:
        The same text.
    """
    return message


def get_date() -> str:
    """Return the current date and time as an ISO-8601 string."""
    return datetime.now().isoformat(timespec="seconds")


def calculate(expression: str) -> str:
    """Evaluate a simple arithmetic expression and return the result.

    Args:
        expression: A Python arithmetic expression, e.g. '2 + 3 * 4'.

    Returns:
        The numeric result as a string, or an error message.
    """
    # Restrict builtins to prevent code injection
    try:
        result = eval(expression, {"__builtins__": {}}, {})  # noqa: S307
        return str(result)
    except Exception as exc:
        return f"Error: {exc}"


BUILTIN_TOOLS: List[FunctionTool] = [
    FunctionTool(echo),
    FunctionTool(get_date),
    FunctionTool(calculate),
]


# ---------------------------------------------------------------------------
# ADKAgentConfig  (kept for backwards compatibility with __init__.py)
# ---------------------------------------------------------------------------

class ADKAgentConfig:
    """Lightweight config dataclass — mirrors the old interface."""

    def __init__(
        self,
        name: str,
        description: str,
        model: str = "gemini-2.5-flash",
        instructions: str = "",
        tools: List[str] | None = None,
    ):
        self.name = name
        self.description = description
        self.model = model
        self.instructions = instructions
        self.tools = tools or []


# ---------------------------------------------------------------------------
# ADKAgentBase  (thin shim — real logic lives in LlmAgent)
# ---------------------------------------------------------------------------

class ADKAgentBase:
    """
    Wraps an ADK LlmAgent with a minimal backwards-compatible interface.

    Subclasses call super().__init__() and then access self.agent (LlmAgent)
    and self.runner (Runner) directly.
    """

    def __init__(self, config: ADKAgentConfig, api_key: str | None = None, tools: List[FunctionTool] | None = None):
        self.config = config
        model = _make_model(api_key)

        # Combine builtin tools with provided dynamic tools
        all_tools = BUILTIN_TOOLS + (tools or [])

        self.agent = LlmAgent(
            name=config.name,
            model=model,
            description=config.description,
            instruction=config.instructions,
            tools=all_tools,
            output_key="result",
        )

        session_service = InMemorySessionService()
        self.runner = Runner(
            agent=self.agent,
            app_name=config.name,
            session_service=session_service,
        )

    async def generate(self, prompt: str, session_id: str = "default") -> str:
        """Send a prompt and return the text response."""
        try:
            session = await self.runner.session_service.get_session(app_name=self.config.name, user_id="user", session_id=session_id)
            if not session:
                await self.runner.session_service.create_session(app_name=self.config.name, user_id="user", session_id=session_id)
        except Exception:
            await self.runner.session_service.create_session(app_name=self.config.name, user_id="user", session_id=session_id)

        content = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=prompt)],
        )
        full_response: List[str] = []
        async for event in self.runner.run_async(
            user_id="user",
            session_id=session_id,
            new_message=content,
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        full_response.append(part.text)
        return "".join(full_response)


from backend.models.schemas import IntentClassification, WorkflowType, Plan, ReasoningStep

class IntentClassifierAgent(ADKAgentBase):
    """
    Routes user messages to one of four workflows using Gemini 2.5 Flash.

    Workflows:
      • data_analysis  — data queries, analytics, charts, reports
      • code_gen       — writing, debugging, or reviewing code
      • research       — information search, summarisation, fact-finding
      • general_chat   — everything else
    """

    def __init__(self, api_key: str | None = None):
        config = ADKAgentConfig(
            name="intent_classifier",
            description="Classifies user intent and routes to the appropriate workflow.",
            instructions="""You are an intent classification agent for an enterprise AI platform.

Analyse the user message and return ONLY a JSON object — no markdown, no explanation.

Available workflows:
- data_analysis : data queries, analytics, charts, statistics, database operations
- code_gen      : writing, debugging, reviewing, explaining, or refactoring code
- research      : web searches, summarisation, fact-finding, "what is / how does" questions
- general_chat  : casual conversation and anything that doesn't fit the above

Required JSON schema:
{
  "workflow": "<workflow_name>",
  "confidence": <float 0.0–1.0>,
  "reasoning": "<one sentence>",
  "suggested_tools": ["<tool_name>", ...]
}""",
        )
        super().__init__(config, api_key)

    async def classify(self, user_message: str) -> IntentClassification:
        """Return a classification dict for *user_message* using semantic understanding."""
        import json

        # Attempt primary LLM classification
        response = await self.generate(f"Classify this message: {user_message}")
        try:
            # Robust JSON parsing
            text = response.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(text)
            
            # Validate essential keys
            if "workflow" in result and "confidence" in result:
                return IntentClassification(
                    workflow=WorkflowType(result["workflow"]),
                    confidence=result["confidence"],
                    reasoning=result.get("reasoning", ""),
                    suggested_tools=result.get("suggested_tools", [])
                )
            
            raise ValueError("Incomplete JSON response from LLM")
            
        except (json.JSONDecodeError, ValueError, IndexError) as e:
            # Semantic fallback (Zero Brittle Development: NO KEYWORDS)
            return await self._semantic_fallback(user_message)

    async def _semantic_fallback(self, message: str) -> IntentClassification:
        """
        Fallback using a simplified semantic prompt when JSON parsing fails.
        Strictly avoids keyword matching.
        """
        prompt = (
            f"The user said: '{message}'.\n"
            "Based on the intent, which single workflow is most appropriate?\n"
            "Options: data_analysis, code_gen, research, general_chat.\n"
            "Reply with ONLY the workflow name."
        )
        
        workflow = await self.generate(prompt)
        workflow = workflow.strip().lower()
        
        # Map response to valid workflow
        valid_workflows = ["data_analysis", "code_gen", "research", "general_chat"]
        matched_workflow = "general_chat"
        for wf in valid_workflows:
            if wf in workflow:
                matched_workflow = wf
                break
                
        return IntentClassification(
            workflow=WorkflowType(matched_workflow),
            confidence=0.5,
            reasoning="Semantic fallback triggered due to parsing error.",
            suggested_tools=[]
        )


class WorkflowPlannerAgent(ADKAgentBase):
    """
    Decomposes a user request into an ordered list of executable steps.

    The agent uses chain-of-thought reasoning internally (ADK handles the
    ReAct loop) and returns a structured JSON plan.
    """

    def __init__(self, api_key: str | None = None):
        config = ADKAgentConfig(
            name="workflow_planner",
            description="Breaks down user requests into clear, tool-ready execution steps.",
            instructions="""You are a task-planning agent for an enterprise AI platform.

Given a user request, a workflow type, and a list of available tools, create a
step-by-step execution plan.  Return ONLY a JSON object — no markdown, no prose.

Required JSON schema:
{
  "goal": "<one-sentence goal>",
  "steps": [
    {
      "step_number": <int>,
      "description": "<what this step does>",
      "tool_used": "<tool_name or null>",
      "tool_input": {<key: value> or null}
    }
  ]
}""",
        )
        super().__init__(config, api_key)

    async def create_plan(
        self,
        user_message: str,
        workflow: str,
        available_tools: List[str],
    ) -> Plan:
        """Return a plan dict for *user_message* given *workflow* and *available_tools*."""
        import json

        tools_block = "\n".join(f"- {t}" for t in available_tools) or "- (none)"
        prompt = (
            f"User request: {user_message}\n"
            f"Workflow: {workflow}\n"
            f"Available tools:\n{tools_block}\n\n"
            "Create a JSON execution plan."
        )
        response = await self.generate(prompt)
        try:
            text = response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            result = json.loads(text)
            
            steps = []
            for s in result.get("steps", []):
                steps.append(ReasoningStep(
                    step_number=s.get("step_number", len(steps) + 1),
                    description=s.get("description", ""),
                    tool_used=s.get("tool_used"),
                    tool_input=s.get("tool_input")
                ))
            
            return Plan(goal=result.get("goal", user_message), steps=steps)
        except (json.JSONDecodeError, ValueError):
            return self._simple_plan(user_message, workflow, available_tools)

    def _simple_plan(
        self,
        user_message: str,
        workflow: str,
        available_tools: List[str],
    ) -> Plan:
        if workflow == "general_chat" or not available_tools:
            steps = [ReasoningStep(step_number=1, description="Respond directly to the user.",
                      tool_used=None, tool_input=None)]
        else:
            steps = [
                ReasoningStep(step_number=i, description=f"Execute {tool}.",
                 tool_used=tool, tool_input={"query": user_message})
                for i, tool in enumerate(available_tools[:3], 1)
            ]
        return Plan(goal=user_message, steps=steps)


class ToolExecutorAgent(ADKAgentBase):
    """
    Executes tools on behalf of the orchestrator.

    Built-in tools (echo, get_date, calculate) are registered as ADK
    FunctionTools on the underlying LlmAgent.  Custom skills passed via
    *tools* are registered as well.
    """

    def __init__(self, tools: List[FunctionTool] | None = None, api_key: str | None = None):
        config = ADKAgentConfig(
            name="tool_executor",
            description="Executes tools and returns structured results.",
            instructions=(
                "You are a tool-execution agent. "
                "When asked to run a tool, call it and return the result as plain text."
            ),
        )
        super().__init__(config, api_key, tools=tools)
        # Store tools by name for potential manual dispatch or lookup
        self.dynamic_tools: Dict[str, FunctionTool] = {t.name: t for t in (tools or [])}

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Any:
        """
        Execute *tool_name* with *arguments*.

        This method now primarily serves as a compatibility shim. ADK's Runner
        handles tool dispatch automatically, but this can be used for manual
        calls.
        """
        from backend.models.schemas import ToolCallResponse
        # Look for the tool in the agent's registered tools
        # LlmAgent stores tools in self.agent.tools
        all_tools = {t.name: t for t in self.agent.tools}
        
        if tool_name in all_tools:
            try:
                # Execute the tool function
                tool = all_tools[tool_name]
                result = tool.func(**arguments)
                return ToolCallResponse(tool_name=tool_name, success=True, result=result)
            except Exception as exc:
                return ToolCallResponse(tool_name=tool_name, success=False, result=None, error=str(exc))

        return ToolCallResponse(
            tool_name=tool_name,
            success=False,
            result=None,
            error=f"Tool '{tool_name}' not found.",
        )

    def register_tool(self, tool: FunctionTool) -> None:
        """Register an external tool at runtime."""
        self.agent.tools.append(tool)
        self.dynamic_tools[tool.name] = tool

    def available_tools(self) -> List[str]:
        return [t.name for t in self.agent.tools]


# ---------------------------------------------------------------------------
# Workflow orchestration agents  (thin ADK wrappers)
# ---------------------------------------------------------------------------

class SequentialWorkflowAgent:
    """
    Wraps ADK's SequentialAgent.

    Sub-agents run one after another; each receives the previous agent's
    output via shared ADK session state (output_key → input).
    """

    def __init__(self, name: str, sub_agents: List[ADKAgentBase], api_key: str | None = None):
        self.name = name
        self._adk_agent = SequentialAgent(
            name=name,
            sub_agents=[a.agent for a in sub_agents],
        )
        session_service = InMemorySessionService()
        self._runner = Runner(
            agent=self._adk_agent,
            app_name=name,
            session_service=session_service,
        )

    async def execute(self, user_message: str, session_id: str = "default") -> str:
        content = genai_types.Content(
            role="user", parts=[genai_types.Part(text=user_message)]
        )
        parts: List[str] = []
        async for event in self._runner.run_async(
            user_id="user", session_id=session_id, new_message=content
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        parts.append(part.text)
        return "".join(parts)


class ParallelWorkflowAgent:
    """
    Wraps ADK's ParallelAgent.

    All sub-agents receive the same input and run concurrently; results are
    collected in session state under each agent's output_key.
    """

    def __init__(self, name: str, sub_agents: List[ADKAgentBase], api_key: str | None = None):
        self.name = name
        self._adk_agent = ParallelAgent(
            name=name,
            sub_agents=[a.agent for a in sub_agents],
        )
        session_service = InMemorySessionService()
        self._runner = Runner(
            agent=self._adk_agent,
            app_name=name,
            session_service=session_service,
        )

    async def execute(self, user_message: str, session_id: str = "default") -> str:
        content = genai_types.Content(
            role="user", parts=[genai_types.Part(text=user_message)]
        )
        parts: List[str] = []
        async for event in self._runner.run_async(
            user_id="user", session_id=session_id, new_message=content
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        parts.append(part.text)
        return "".join(parts)


class LoopWorkflowAgent:
    """
    Wraps ADK's LoopAgent.

    The sub-agents iterate until *max_iterations* is reached or until one
    of them sets the ADK escalate flag.
    """

    def __init__(
        self,
        name: str,
        sub_agents: List[ADKAgentBase],
        max_iterations: int = 5,
        api_key: str | None = None,
    ):
        self.name = name
        self._adk_agent = LoopAgent(
            name=name,
            sub_agents=[a.agent for a in sub_agents],
            max_iterations=max_iterations,
        )
        session_service = InMemorySessionService()
        self._runner = Runner(
            agent=self._adk_agent,
            app_name=name,
            session_service=session_service,
        )

    async def execute(self, user_message: str, session_id: str = "default") -> str:
        content = genai_types.Content(
            role="user", parts=[genai_types.Part(text=user_message)]
        )
        parts: List[str] = []
        async for event in self._runner.run_async(
            user_id="user", session_id=session_id, new_message=content
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        parts.append(part.text)
        return "".join(parts)


# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------

_intent_classifier: Optional[IntentClassifierAgent] = None
_workflow_planner: Optional[WorkflowPlannerAgent] = None
_tool_executor: Optional[ToolExecutorAgent] = None


def get_intent_classifier(api_key: str | None = None) -> IntentClassifierAgent:
    global _intent_classifier
    if _intent_classifier is None:
        _intent_classifier = IntentClassifierAgent(api_key)
    return _intent_classifier


def get_workflow_planner(api_key: str | None = None) -> WorkflowPlannerAgent:
    global _workflow_planner
    if _workflow_planner is None:
        _workflow_planner = WorkflowPlannerAgent(api_key)
    return _workflow_planner


def get_tool_executor(
    tools: List[FunctionTool] | None = None, api_key: str | None = None
) -> ToolExecutorAgent:
    global _tool_executor
    if _tool_executor is None:
        _tool_executor = ToolExecutorAgent(tools, api_key)
    return _tool_executor
