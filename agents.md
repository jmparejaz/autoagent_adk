# Enterprise Agentic Platform - Agents Documentation

## Overview

The Enterprise Agentic Platform is a multi-agent system that uses Google ADK-style architecture to route user intents to specific workflows, decompose complex tasks using a reasoning engine, and execute dynamic tools defined in a markdown-based skill store.

## Architecture

The system consists of several key agents that work together to process user requests:

### 1. Intent Classifier Agent

**Purpose**: Classifies user intent and routes to appropriate workflows.

**Location**: `backend/agents/adk_agents.py`

**Functionality**:
- Analyzes user messages to determine the best workflow
- Uses LLM-based classification with fallback to rule-based classification
- Returns workflow assignment with confidence score and reasoning
- Available workflows: data_analysis, code_gen, research, general_chat

**Key Methods**:
- `classify(user_message: str) -> Dict[str, Any]`: Classifies user intent
- `_rule_based_classify(message: str) -> Dict[str, Any]`: Fallback classification

### 2. Workflow Planner Agent

**Purpose**: Decomposes tasks into executable steps using chain-of-thought reasoning.

**Location**: `backend/agents/adk_agents.py`

**Functionality**:
- Creates detailed execution plans with reasoning steps
- Specifies what needs to be done, which tool to use, and expected input/output
- Returns JSON plan with goal and steps

**Key Methods**:
- `create_plan(user_message: str, workflow: str, available_tools: List[str]) -> Dict[str, Any]`: Creates execution plan
- `_create_simple_plan(user_message: str, workflow: str, available_tools: List[str]) -> Dict[str, Any]`: Fallback simple plan

### 3. Tool Executor Agent

**Purpose**: Executes tools and manages tool outputs.

**Location**: `backend/agents/adk_agents.py`

**Functionality**:
- Executes both built-in tools and dynamically loaded skill tools
- Handles tool execution and returns results
- Manages errors and tool not found scenarios

**Key Methods**:
- `execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]`: Executes a tool
- `_execute_skill(skill: Any, arguments: Dict[str, Any]) -> Any`: Executes a skill

**Built-in Tools**:
- `echo`: Echoes back the input
- `get_date`: Returns current date and time
- `calculate`: Performs calculations

### 4. Sequential Workflow Agent

**Purpose**: Executes sub-agents in a fixed order.

**Location**: `backend/agents/adk_agents.py`

**Functionality**:
- Mirrors ADK's SequentialAgent pattern
- Executes sub-agents sequentially, passing output to next agent

**Key Methods**:
- `execute(initial_input: Any) -> Any`: Executes sub-agents sequentially

### 5. Parallel Workflow Agent

**Purpose**: Executes sub-agents simultaneously.

**Location**: `backend/agents/adk_agents.py`

**Functionality**:
- Mirrors ADK's ParallelAgent pattern
- Executes all sub-agents in parallel and returns combined results

**Key Methods**:
- `execute(input_data: Any) -> List[Any]`: Executes sub-agents in parallel

### 6. Loop Workflow Agent

**Purpose**: Executes sub-agents iteratively until termination condition.

**Location**: `backend/agents/adk_agents.py`

**Functionality**:
- Mirrors ADK's LoopAgent pattern
- Executes sub-agents in a loop until condition is met

**Key Methods**:
- `execute(initial_input: Any) -> Any`: Executes sub-agents in a loop

## Skill Loader

**Purpose**: Loads and manages skills from markdown files.

**Location**: `backend/skills/skill_loader.py`

**Functionality**:
- Scans `.skills` directory for markdown files
- Parses YAML frontmatter for metadata
- Extracts execution code from markdown body
- Builds skill objects and registers them

**Key Methods**:
- `load_skills() -> Dict[str, Skill]`: Loads all skills
- `_parse_skill_file(file_path: Path) -> Optional[Skill]`: Parses a single skill file
- `get_skill(tool_name: str) -> Optional[Skill]`: Gets a specific skill
- `reload()`: Reloads all skills

## Data Models

**Location**: `backend/models/schemas.py`

### Key Models:

1. **IntentClassification**: Intent classification result with workflow, confidence, reasoning, and suggested tools
2. **ReasoningStep**: A single reasoning step with step number, description, tool used, input, output, and status
3. **Plan**: Execution plan with goal, steps, current step, and completion status
4. **Skill**: Skill/tool definition with tool name, description, arguments, execution code, and category
5. **Message**: Chat message with ID, role, content, timestamp, reasoning steps, and tools used
6. **Session**: Chat session with ID, workflow, messages, and timestamps
7. **ChatRequest**: Chat request payload with message, session ID, and workflow override
8. **ChatResponse**: Chat response payload with message, intent, plan, and session ID
9. **ToolCallRequest**: Request to execute a specific tool with tool name and arguments
10. **ToolCallResponse**: Response from tool execution with tool name, success, result, and error

## Workflow Definitions

### 1. Data Analysis Workflow

**Purpose**: Analyze data, generate insights

**Tools**: Data Query, Chart Generator, Report Builder

**Location**: `backend/workflows/data_analysis.py`

### 2. Code Generation Workflow

**Purpose**: Write, review, and debug code

**Tools**: Code Writer, Code Reviewer, Bug Detector

**Location**: `backend/workflows/code_gen.py`

### 3. Research Workflow

**Purpose**: Search and summarize information

**Tools**: Web Search, Content Summarizer, Citation Generator

**Location**: `backend/workflows/research.py`

### 4. General Chat Workflow

**Purpose**: General conversation and assistance

**Tools**: None (pure LLM conversation)

**Location**: `backend/workflows/general_chat.py`

## Data Flow

1. **Input**: User sends message
2. **Intent**: Classifier labels with workflow
3. **Plan**: Planner creates steps
4. **Execution**: System loops through steps with tool execution
5. **Output**: Final response

## Edge Cases

- **Ambiguous Intent**: If confidence < 60%, ask clarifying question
- **Tool Failure**: Planner catches error, attempts retry or alternative
- **Hallucination Check**: Verify tool outputs before referencing

## API Endpoints

### REST Endpoints

- `POST /api/chat` - Send message and get response
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{id}` - Get session history
- `POST /api/workflows` - List available workflows
- `GET /api/skills` - List available skills/tools

### WebSocket Endpoint

- `WS /ws/chat` - Real-time streaming of reasoning steps

## Project Structure

```
/workspace/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── intent_classifier.py
│   │   ├── workflow_planner.py
│   │   └── tool_executor.py
│   ├── skills/
│   │   ├── __init__.py
│   │   └── skill_loader.py
│   ├── workflows/
│   │   ├── __init__.py
│   │   ├── data_analysis.py
│   │   ├── code_gen.py
│   │   ├── research.py
│   │   └── general_chat.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── stores/
│   │   ├── styles/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   │   ├── logo.svg
│   │   └── mascot/
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .skills/
│   ├── data_query.md
│   ├── chart_generator.md
│   ├── code_writer.md
│   ├── web_search.md
│   └── summarizer.md
└── README.md
```

## Acceptance Criteria

### Test Scenarios

1. **System Startup & Skill Loading**: Create dummy `test_skill.md`, start system, verify skill appears in registered tool list
2. **Intent Classification**: Test various inputs to ensure correct workflow routing
3. **Reasoning Trace**: Verify UI shows "Thinking" accordion with intermediate steps
4. **Branding Verification**: Verify logo, colors, and mascot appear correctly

### Acceptance Criteria

- System successfully routes queries to correct workflow
- Adding `.md` file to `.skills` makes tool available
- WebUI is fully decoupled from standard CLI interface
- Complete task execution history is logged