# Enterprise Agentic Platform

## Project Overview

The **Enterprise Agentic Platform** is a multi-agent system that combines Google's Agent Development Kit (ADK) with a custom, parametric agentic architecture. It dynamically routes user intents to specialized workflows, decomposes complex tasks using a reasoning engine, and executes tools defined in a markdown-based skill store. The platform includes a custom, white-labelable React web interface that displays the agent's real-time reasoning trace.

### Architecture & Tech Stack
- **Backend**: Python 3.10+, FastAPI, Google ADK (`google-adk`), Gemini 2.5 Flash model.
- **Frontend**: React 18, Vite, Zustand (State Management), WebSocket (Real-time streaming).
- **Core Paradigm**: 
  - **Dynamic Skills**: Skills are defined in markdown files (`.skills/*.md`) and are dynamically loaded and converted to ADK `FunctionTool`s at runtime.
  - **Workflow-as-Skill**: Workflows are first-class citizens, dynamically composable, and can be used as tools by other agents.
  - **Hybrid ADK Integration**: The system is transitioning from a custom framework to a Google ADK-centric architecture using an adapter layer (`adk_adapter.py`) to preserve dynamic, parametric agent creation while leveraging ADK's robustness.

## Directory Structure & Key Files

- `run.py`: The main CLI entry point to start the backend server, allowing customization of branding and configuration via arguments.
- `backend/`: Contains the FastAPI application and core agent logic.
  - `backend/agents/`: Core agent components, including ADK-enhanced agents (`adk_agents.py`) and the ADK adapter layer (`adk_adapter.py`).
  - `backend/skills/`: Logic for loading and managing tools (`skill_loader.py` dynamically parses `.md` skills).
  - `backend/workflows/`: Specific workflow implementations (Data Analysis, Code Gen, Research, General Chat).
- `frontend/`: The React web interface.
- `.skills/`: The markdown-based skill store. Drop `.md` files here to dynamically add capabilities.
- `docker-compose.yml` / `Dockerfile`: Containerization setup for deployment.
- `SPEC.md`, `agents.md`, `GOOGLE_ADK_INTEGRATION_PLAN.md`, `ADK_INTEGRATION_LESSONS_LEARNED.md`: Critical documentation on architecture, integration plans, and development philosophy.

## Building and Running

### Prerequisites
You must set your Google or Gemini API key to run the platform:
```bash
export GOOGLE_API_KEY='your-api-key'
# OR
export GEMINI_API_KEY='your-api-key'
```

### Using Docker (Recommended for Deployment)
The easiest way to run the platform is via Docker Compose. All dependencies (including ADK) are managed within the container environment.
```bash
# Build and start the containers
docker-compose up --build

# Run in background
docker-compose up -d

# Stop the containers
docker-compose down
```

### Local Development
To run the project locally:

**Backend:**
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server (defaults to http://0.0.0.0:8000)
python run.py

# Optional: run with debug mode or custom config
python run.py --debug
python run.py --config config.yaml
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev    # Start the Vite development server
npm run build  # Build the frontend for production (served by FastAPI)
```
*Note: The FastAPI application serves the frontend from `frontend/dist/index.html` on its root endpoint when built.*

## Development Conventions & Philosophy

- **Zero Brittle Development**: This is an enterprise-grade system. Naive approaches like keyword-based intent classification (e.g., `if "data" in message: ...`), hardcoded tool lists, and brittle JSON parsing are strictly forbidden. You must use semantic LLM understanding, robust validation schemas, and comprehensive error handling with fallbacks.
- **Parametric Agent Creation**: Do not create static, hardcoded tool implementations. The system relies on dynamic tool discovery. Ensure that new skills are created as `.md` files in the `.skills/` directory and workflows are registered dynamically so they can be treated as tools.
- **ADK Adapter Pattern**: When working with Google ADK, always utilize the adapter layer (`adk_adapter.py`). Skills and workflows must be automatically converted to ADK `FunctionTool`s (e.g., `markdown_skill_to_adk_tool()`, `workflow_to_adk_tool()`) to maintain the system's flexible, composable nature. Do not instantiate static `FunctionTool` lists directly in the agents.
- **Hybrid Operation Mode**: When refactoring, ensure backward compatibility. Both the legacy custom systems and the new ADK integrations must be capable of running simultaneously to provide fallback mechanisms during the migration.
