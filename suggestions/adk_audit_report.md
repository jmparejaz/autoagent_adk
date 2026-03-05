# ADK Agent Codebase Audit & Refactor

## What Was Found

### The Core Problem: ADK in Name Only

The codebase presented itself as a Google ADK implementation — the package was named `adk_agents`, classes were called `IntentClassifierAgent`, `SequentialWorkflowAgent`, and so on — but none of it actually used the Google Agent Development Kit.

The `adk_agents.py` file attempted to import from `google.genkit`, which is a Node.js library with no Python equivalent. When that import failed (as it always would), the code silently fell back to calling `google.generativeai` directly. The result was a hand-rolled agent framework dressed up in ADK terminology, with none of ADK's actual capabilities.

The three legacy files — `intent_classifier.py`, `workflow_planner.py`, and `tool_executor.py` — were doing the same job from the other direction: real working code, but entirely custom-built, reimplementing things ADK already provides.

---

## File-by-File Breakdown

### `adk_agents.py` — Broken ADK Facade

The file opened with:

```python
from google.genkit import Genkit
from google.genkit.plugins import GoogleAI
```

This import always fails in Python. The `try/except` block caught the error silently and printed a warning, meaning every deployment was running in degraded fallback mode without any obvious signal.

The agent classes that followed — `IntentClassifierAgent`, `WorkflowPlannerAgent`, `ToolExecutorAgent` — were wrapping raw `GenerativeModel.generate_content()` calls and manually parsing JSON out of the responses. The `SequentialWorkflowAgent`, `ParallelWorkflowAgent`, and `LoopWorkflowAgent` classes were hand-written execution loops, not ADK primitives.

**In short:** this file was a from-scratch agent framework that happened to share names with ADK concepts.

### `intent_classifier.py` — Working but Redundant

A functional intent classifier with two modes: LLM-based (calling `model.generate_content()` directly) and rule-based keyword matching as a fallback. The logic was sound, but it duplicated what an ADK `LlmAgent` with a well-written instruction prompt handles natively — including the reasoning loop, retry logic, and tool dispatch.

### `workflow_planner.py` — Reimplementing ADK's Core

This file manually decomposed tasks into `ReasoningStep` objects and tracked their status in a `Plan` object. This is precisely what ADK's `SequentialAgent` and `ParallelAgent` do internally. The schema (`Plan`, `ReasoningStep`, `current_step`, `is_complete`) was a bespoke reimplementation of ADK's built-in session state and event system.

### `tool_executor.py` — Registry Pattern ADK Doesn't Need

A custom tool registry with a `_tool_registry` dict, manual dispatch logic, and a `register_custom_tool()` method. ADK's `FunctionTool` replaces all of this: tools are plain Python functions with docstrings and type hints, and ADK generates their schemas and handles dispatch automatically.

The file also contained a `calculate` tool using `eval()` with a production warning comment that had never been acted on.

### `__init__.py` — Exporting Both Systems

The package's `__init__.py` exported both the ADK-named classes and the legacy classes side by side, under aliases like `get_legacy_intent_classifier`. This suggested the author knew both systems existed but had no clear migration path between them.

---

## What Was Changed

### `adk_agents.py` — Rewritten Against Real ADK

The file now imports from `google.adk` correctly:

```python
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
```

Key changes:

- **Model initialisation** uses `LiteLlm(model="gemini/gemini-2.5-flash", api_key=key)`, the correct ADK pattern for Gemini API key auth (as opposed to Vertex AI service account auth).
- **`IntentClassifierAgent` and `WorkflowPlannerAgent`** are now genuine `LlmAgent` instances. Their logic lives in instruction prompts; ADK handles the ReAct loop, tool dispatch, and session state.
- **Built-in tools** (`echo`, `get_date`, `calculate`) are plain Python functions wrapped with `FunctionTool`. ADK introspects their signatures and docstrings to generate tool schemas automatically — no registry, no manual dispatch.
- **`SequentialWorkflowAgent`, `ParallelWorkflowAgent`, `LoopWorkflowAgent`** wrap the actual ADK `SequentialAgent`, `ParallelAgent`, and `LoopAgent` primitives, using a shared `Runner` and `InMemorySessionService` per agent.
- The silent `try/except` import failure is gone. If `google-adk` is not installed, the import fails loudly and immediately.

### `__init__.py` — Cleaned Up

All legacy exports removed. The package now exports only the ADK-native classes and the `BUILTIN_TOOLS` list (useful for extending tool sets in subclasses).

---

## What to Do Next

**Delete the legacy files** once any remaining callers have been migrated:
- `intent_classifier.py`
- `workflow_planner.py`
- `tool_executor.py`

**Install the real dependency:**
```bash
pip install google-adk
```

**Set your API key** via environment variable or pass it explicitly:
```bash
export GEMINI_API_KEY=your_key_here
```

**Replace `eval()` in the `calculate` tool** with a proper math parser for production:
```bash
pip install simpleeval
```

**Consider persistent session storage** — `InMemorySessionService` is fine for development but loses state on restart. ADK supports pluggable session backends for production.

---

## Summary

The codebase had a working custom agent framework and a broken ADK facade living side by side, with the `__init__.py` exporting both and obscuring which one was actually running. The refactor removes the custom framework entirely and grounds everything in real ADK primitives — the intent classification, planning, tool execution, and workflow orchestration that were all being reimplemented manually are now delegated to the library that was always supposed to be handling them.
