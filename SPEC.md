# Enterprise Agentic Platform Specification

## 1. Project Overview

**Project Name**: Enterprise Agentic Platform
**Project Type**: AI Agent Orchestration System with Custom Web Interface
**Core Functionality**: A multi-agent system utilizing Google ADK-style architecture to route user intents to specific workflows, decompose complex tasks using a reasoning engine, and execute dynamic tools defined in a markdown-based skill store.
**Target Users**: Internal enterprise employees, operations teams, and data analysts

---

## 2. Architecture & Tech Stack

### Backend Stack
- **Framework**: Google ADK-style Agent Architecture (Custom Implementation)
- **Language**: Python 3.10+
- **Server**: FastAPI (to wrap the ADK agents and serve the custom UI)
- **Model**: Gemini 2.0 Flash (optimized for reasoning and tool use)
- **Database**: SQLite (for session history and workflow state)

### Frontend Stack
- **Framework**: React 18 + Vite
- **State Management**: Zustand
- **Communication**: WebSocket (for real-time streaming of reasoning steps)
- **Styling**: CSS Modules with CSS Variables

---

## 3. UI/UX Specification

### Layout Structure
- **Sidebar (Left)**:
  - Brand Header with Company Logo & Name
  - Workflow Selector (Auto-detected by Intent, but manually overrideable)
  - History: List of past sessions
  - Mascot Area: Bottom left placement for company mascot
- **Main Stage (Center)**:
  - Chat Interface: Bubble layout
  - Thought Process Collapsible: "Thinking..." accordions to show task decomposition steps
  - Input Area: Text input + Attachment clip + "Run" button
- **Tool Panel (Right - Collapsible)**:
  - Live view of tools being executed
  - Debug console

### Visual Design
- **Color Palette (Custom Branding)**:
  - Primary: `#0F52BA` (Sapphire Blue - Enterprise Trust)
  - Secondary: `#50C878` (Emerald Green - Success/Active)
  - Background: `#F8F9FA` (Light Gray) / `#1A1A2E` (Dark Mode)
  - Accent: `#FFD700` (Gold - Mascot/Highlights)
  - Text Primary: `#2D3748` / `#E2E8F0` (Dark mode)
  - Text Secondary: `#718096` / `#A0AEC0` (Dark mode)
  - Border: `#E2E8F0` / `#4A5568` (Dark mode)
- **Typography**:
  - UI Elements: Inter, system-ui, sans-serif
  - Code/Tool logs: JetBrains Mono, monospace
- **Spacing System**: 4px base unit (4, 8, 12, 16, 24, 32, 48, 64)
- **Border Radius**: 8px (cards), 12px (modals), 20px (buttons)

### Components

#### Chat Bubbles
- User messages: Right-aligned, Primary color background, white text
- Agent messages: Left-aligned, White background (light mode) / #2D3748 (dark mode), with subtle shadow
- Timestamp below each message, smaller font, secondary color

#### Thought Process Panel
- Collapsible accordion with smooth animation
- Shows reasoning steps in numbered list format
- Each step shows: Step number, Description, Tool used (if any)
- Subtle left border in accent color

#### Mascot Animation
- Idle: Static SVG with subtle floating animation
- Thinking: Animated thinking bubbles appearing
- Speaking: Subtle bounce animation
- Error: Sad expression with recovery prompt

#### Input Area
- Large textarea with placeholder "Ask anything..."
- Attachment button (left)
- Send button (right) with primary color
- Character counter (optional)

---

## 4. Component Architecture

### Backend Components

#### 1. Skill Loader (Tool System)
- **Directory**: `./.skills/*.md`
- **Function**: On startup, scan this directory
- **Mechanism**:
  - Parse Frontmatter (YAML) for metadata: `tool_name`, `description`, `arguments`
  - Parse Body for content: `execution_logic` or `api_endpoint`
  - Register dynamically as function tools within the agent

#### 2. Intent Classifier (Entry Node)
- **Type**: Lightweight Router Agent
- **Prompt Strategy**: "Given the user input, classify it into one of the following workflows: [Data_Analysis, Code_Gen, Research, General_Chat]. Return only the workflow ID."
- **Output**: Workflow Configuration Object

#### 3. Planner Node (Decomposition)
- **Logic**: Chain-of-Thought (CoT) implementation
- **Prompt Loop**:
  1. Analyze the user goal
  2. Break into sub-tasks (Step 1, Step 2, ...)
  3. For the current step, identify if a tool is needed
  4. Hand off to Tool Executor

#### 4. Tool Executor
- **Logic**: Receives tool call request from the Planner
- **Action**: Matches request to loaded `.skills` dictionary
- **Execution**: Runs the Python function or API call defined in the skill
- **Feedback**: Returns output observation back to the Planner

---

## 5. Functionality Specification

### Core Features

1. **Dynamic Intent Routing**
   - System automatically switches context based on query
   - Example: "Analyze Q3 revenue" → Data_Analysis Workflow

2. **Markdown Skill Definition**
   - Developers can add new capabilities by dropping `.md` file into folder
   - Hot-reloading supported

3. **Transparent Reasoning**
   - UI displays why the agent chose a specific tool
   - Shows reasoning trace in real-time

4. **Custom Branding**
   - CSS variables for easy white-labeling
   - Logo and mascot support

### Workflow Definitions

#### 1. Data Analysis Workflow
- **Purpose**: Analyze data, generate insights
- **Tools**: Data Query, Chart Generator, Report Builder

#### 2. Code Generation Workflow
- **Purpose**: Write, review, and debug code
- **Tools**: Code Writer, Code Reviewer, Bug Detector

#### 3. Research Workflow
- **Purpose**: Search and summarize information
- **Tools**: Web Search, Content Summarizer, Citation Generator

#### 4. General Chat Workflow
- **Purpose**: General conversation and assistance
- **Tools**: None (pure LLM conversation)

### Data Flow
1. **Input**: User sends message
2. **Intent**: Classifier labels with workflow
3. **Plan**: Planner creates steps
4. **Execution**: System loops through steps with tool execution
5. **Output**: Final response

### Edge Cases
- **Ambiguous Intent**: If confidence < 60%, ask clarifying question
- **Tool Failure**: Planner catches error, attempts retry or alternative
- **Hallucination Check**: Verify tool outputs before referencing

---

## 6. API Endpoints

### REST Endpoints
- `POST /api/chat` - Send message and get response
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{id}` - Get session history
- `POST /api/workflows` - List available workflows
- `GET /api/skills` - List available skills/tools

### WebSocket Endpoint
- `WS /ws/chat` - Real-time streaming of reasoning steps

---

## 7. Project Structure

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
│   └──summarizer.md
└── README.md
```

---

## 8. Acceptance Criteria

### Test Scenarios
1. **System Startup & Skill Loading**
   - Create dummy `test_skill.md`
   - Start system
   - Verify skill appears in registered tool list

2. **Intent Classification**
   - Input: "Reset my password" → Expected: `IT_SUPPORT_WORKFLOW`
   - Input: "Write a poem" → Expected: `GENERAL_CHAT_WORKFLOW`

3. **Reasoning Trace**
   - Ask multi-step question
   - Verify UI shows "Thinking" accordion with intermediate steps

4. **Branding Verification**
   - Verify Logo matches `logo.svg`
   - Verify Primary Buttons are `#0F52BA`
   - Verify Mascot appears during loading states

### Acceptance Criteria
- System successfully routes queries to correct workflow
- Adding `.md` file to `.skills` makes tool available
- WebUI is fully decoupled from standard CLI interface
- Complete task execution history is logged
