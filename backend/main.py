"""
Main FastAPI application for the Enterprise Agentic Platform.
Built with Google Agent Development Kit (ADK) Python Framework.
"""

import os
import json
from datetime import datetime
from typing import Dict, Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.models.schemas import (
    ChatRequest,
    ChatResponse,
    Session,
    Message,
    WorkflowType,
    Skill
)
from backend.skills import get_skill_loader, reload_skills
from backend.agents import (
    get_intent_classifier,
    get_workflow_planner,
    get_tool_executor
)
from backend.workflows import (
    get_workflow_registry,
    register_all_workflows
)
from backend.utils import (
    generate_session_id,
    generate_message_id,
    format_timestamp
)
from backend.config import (
    get_config,
    init_config,
    AppConfig
)


# Initialize components
skill_loader = None
intent_classifier = None
workflow_planner = None
tool_executor = None
workflow_registry = None
app_config: AppConfig = None

# Session storage (in production, use a database)
sessions: Dict[str, Session] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global skill_loader, intent_classifier, workflow_planner, tool_executor, workflow_registry, app_config

    # Initialize configuration
    app_config = get_config()
    print(f"Starting {app_config.branding.project_name}...")
    print(f"Company: {app_config.branding.company_name}")

    # Initialize skill loader with configured skills directory
    skill_loader = get_skill_loader(app_config.skills.skills_dir)
    print(f"Loaded {len(skill_loader.get_all_skills())} skills")

    # Initialize intent classifier
    intent_classifier = get_intent_classifier()

    # Initialize workflow planner
    workflow_planner = get_workflow_planner(
        #skill_loader=skill_loader
        )

    # Initialize tool executor
    tool_executor = get_tool_executor(skill_loader)

    # Register all workflows
    register_all_workflows()
    workflow_registry = get_workflow_registry()
    print(f"Registered {len(workflow_registry.get_all_workflows())} workflows")

    yield

    # Cleanup
    sessions.clear()


# Create FastAPI app
app = FastAPI(
    title="Enterprise Agentic Platform",
    description="AI Agent System with Google ADK Python Framework",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint - serve the web UI."""
    return FileResponse("frontend/dist/index.html")


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": format_timestamp(),
        "skills_count": len(skill_loader.get_all_skills()) if skill_loader else 0,
        "workflows_count": len(workflow_registry.get_all_workflows()) if workflow_registry else 0
    }


@app.get("/api/branding")
async def get_branding():
    """Get branding configuration for the frontend."""
    if not app_config:
        return {
            "company_name": "Agent Platform",
            "project_name": "Enterprise Agentic Platform",
            "tagline": "Powered by Google ADK",
            "primary_color": "#0066B3",
            "secondary_color": "#1E3A8A",
            "accent_color": "#0EA5E9",
            "mascot_name": "Marina",
            "mascot_path": "/mascot"
        }

    return {
        "company_name": app_config.branding.company_name,
        "project_name": app_config.branding.project_name,
        "tagline": app_config.branding.tagline,
        "primary_color": app_config.branding.primary_color,
        "primary_dark": app_config.branding.primary_dark,
        "primary_light": app_config.branding.primary_light,
        "secondary_color": app_config.branding.secondary_color,
        "secondary_dark": app_config.branding.secondary_dark,
        "secondary_light": app_config.branding.secondary_light,
        "accent_color": app_config.branding.accent_color,
        "background_color": app_config.branding.background_color,
        "text_primary": app_config.branding.text_primary,
        "text_secondary": app_config.branding.text_secondary,
        "mascot_name": app_config.branding.mascot_name,
        "mascot_path": app_config.branding.mascot_path,
        "mascot_idle": app_config.branding.mascot_idle,
        "mascot_thinking": app_config.branding.mascot_thinking,
        "mascot_error": app_config.branding.mascot_error
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint - process a user message."""
    try:
        # Get or create session
        session_id = request.session_id or generate_session_id()
        if session_id not in sessions:
            sessions[session_id] = Session(id=session_id)

        session = sessions[session_id]

        # Create user message
        user_message = Message(
            id=generate_message_id(),
            role="user",
            content=request.message
        )
        session.messages.append(user_message)

        # Override workflow if specified
        workflow_type = request.workflow_override
        if not workflow_type:
            # Classify intent
            intent = await intent_classifier.classify(request.message)
            workflow_type = intent.workflow
        else:
            # Create manual intent
            from backend.models.schemas import IntentClassification
            intent = IntentClassification(
                workflow=workflow_type,
                confidence=1.0,
                reasoning="User manually selected workflow"
            )

        session.workflow = workflow_type

        # Get workflow and its tools
        workflow = workflow_registry.get_workflow(workflow_type)
        if not workflow:
            raise HTTPException(status_code=400, detail="Invalid workflow type")

        workflow_tools = workflow.get_available_tools()
        all_tools = list(skill_loader.get_all_skills().values()) + workflow_tools

        # Create execution plan
        plan = await workflow_planner.create_plan(
            request.message,
            intent,
            all_tools
        )

        # Execute workflow
        response_text = await workflow.execute(
            request.message,
            plan,
            tool_executor,
            None  # model - would be Gemini in production
        )

        # Create assistant message
        assistant_message = Message(
            id=generate_message_id(),
            role="assistant",
            content=response_text,
            reasoning_steps=plan.steps,
            tools_used=[step.tool_used for step in plan.steps if step.tool_used]
        )
        session.messages.append(assistant_message)
        session.updated_at = datetime.now()

        return ChatResponse(
            message=assistant_message,
            intent=intent,
            plan=plan,
            session_id=session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
async def list_sessions():
    """List all sessions."""
    return [
        {
            "id": s.id,
            "workflow": s.workflow.value if s.workflow else None,
            "message_count": len(s.messages),
            "created_at": format_timestamp(s.created_at),
            "updated_at": format_timestamp(s.updated_at)
        }
        for s in sessions.values()
    ]


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a specific session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    return {
        "id": session.id,
        "workflow": session.workflow.value if session.workflow else None,
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "timestamp": format_timestamp(m.timestamp),
                "reasoning_steps": [
                    {
                        "step_number": s.step_number,
                        "description": s.description,
                        "tool_used": s.tool_used,
                        "status": s.status
                    }
                    for s in (m.reasoning_steps or [])
                ]
            }
            for m in session.messages
        ],
        "created_at": format_timestamp(session.created_at),
        "updated_at": format_timestamp(session.updated_at)
    }


@app.get("/api/workflows")
async def list_workflows():
    """List all available workflows."""
    if not workflow_registry:
        return []

    workflows = workflow_registry.get_all_workflows()
    return [
        {
            "type": wf.workflow_type.value,
            "name": wf.workflow_type.value.replace("_", " ").title(),
            "description": f"Workflow for {wf.workflow_type.value.replace('_', ' ')} tasks"
        }
        for wf in workflows.values()
    ]


@app.get("/api/skills")
async def list_skills():
    """List all available skills/tools."""
    if not skill_loader:
        return []

    skills = skill_loader.get_all_skills()
    return [
        {
            "tool_name": s.tool_name,
            "description": s.description,
            "category": s.category,
            "arguments": s.arguments
        }
        for s in skills.values()
    ]


@app.post("/api/skills/reload")
async def reload_skills_endpoint():
    """Reload skills from disk."""
    try:
        reload_skills()
        return {"status": "success", "message": "Skills reloaded"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint for real-time streaming
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat with streaming responses."""
    await websocket.accept()

    session_id = None

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            user_message = message_data.get("message", "")
            workflow_override = message_data.get("workflow_override")

            # Create session if needed
            session_id = session_id or generate_session_id()
            if session_id not in sessions:
                sessions[session_id] = Session(id=session_id)

            session = sessions[session_id]

            # Send initial acknowledgment
            await websocket.send_json({
                "type": "start",
                "session_id": session_id,
                "timestamp": format_timestamp()
            })

            # Classify intent
            if workflow_override:
                workflow_type = WorkflowType(workflow_override)
                from backend.models.schemas import IntentClassification
                intent = IntentClassification(
                    workflow=workflow_type,
                    confidence=1.0,
                    reasoning="User manually selected workflow"
                )
            else:
                intent = await intent_classifier.classify(user_message)

            # Send intent classification
            await websocket.send_json({
                "type": "intent",
                "workflow": intent.workflow.value,
                "confidence": intent.confidence,
                "reasoning": intent.reasoning
            })

            # Get workflow
            workflow = workflow_registry.get_workflow(intent.workflow)
            if not workflow:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid workflow"
                })
                continue

            workflow_tools = workflow.get_available_tools()
            all_tools = list(skill_loader.get_all_skills().values()) + workflow_tools

            # Create plan
            plan = await workflow_planner.create_plan(
                user_message,
                intent,
                all_tools
            )

            # Send plan
            await websocket.send_json({
                "type": "plan",
                "goal": plan.goal,
                "steps": [
                    {
                        "step_number": s.step_number,
                        "description": s.description,
                        "tool_used": s.tool_used
                    }
                    for s in plan.steps
                ]
            })

            # Execute workflow step by step
            for i, step in enumerate(plan.steps):
                # Send step start
                await websocket.send_json({
                    "type": "step_start",
                    "step_number": step.step_number,
                    "description": step.description
                })

                # Execute step
                if step.tool_used:
                    tool_args = step.tool_input or {"query": user_message}
                    response = await tool_executor.execute_tool(
                        step.tool_used,
                        tool_args
                    )

                    step.tool_output = response.result
                    step.status = "completed" if response.success else "failed"

                    await websocket.send_json({
                        "type": "step_complete",
                        "step_number": step.step_number,
                        "tool_used": step.tool_used,
                        "result": response.result,
                        "success": response.success
                    })
                else:
                    step.status = "completed"
                    await websocket.send_json({
                        "type": "step_complete",
                        "step_number": step.step_number,
                        "description": step.description,
                        "success": True
                    })

            # Execute workflow to get final response
            response_text = await workflow.execute(
                user_message,
                plan,
                tool_executor,
                None
            )

            # Send final response
            await websocket.send_json({
                "type": "complete",
                "message": response_text,
                "session_id": session_id
            })

    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
    finally:
        if session_id and session_id in sessions:
            # Clean up old sessions after some time
            pass


# Serve static files from frontend dist
frontend_dist = "frontend/dist"
if os.path.exists(frontend_dist):
    # Mount the entire dist directory at root for proper asset serving
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
