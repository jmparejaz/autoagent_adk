"""
Nexus ADK Platform - Main FastAPI Backend
"""
import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn

from backend.config import settings
from backend.agents import initialize_agents
from backend.tools import db_tool, file_tool
from backend.tools.guardrails import guardrails

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Nexus ADK Platform",
    description="Multimodal Agentic System with Google ADK",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
agents = None
active_sessions = {}


# Request/Response Models
class ChatMessage(BaseModel):
    """Chat message model."""
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    """Agent response model."""
    success: bool
    message: str
    agent: str
    data: Optional[Dict[str, Any]] = None
    artifacts: Optional[List[Dict[str, Any]]] = None


class FileUploadResponse(BaseModel):
    """File upload response model."""
    success: bool
    filename: str
    file_type: str
    content: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize agents on startup."""
    global agents
    try:
        agents = initialize_agents()
        logger.info("Nexus ADK Platform started successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")
        # Continue without agents for non-agent endpoints


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    if db_tool:
        db_tool.close()
    logger.info("Nexus ADK Platform shutdown complete")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Nexus ADK Platform",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "chat": "/api/chat",
            "websocket": "/ws/chat",
            "files": "/api/files",
            "database": "/api/db",
            "knowledge": "/api/knowledge"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents_initialized": agents is not None
    }


# ==================== Chat Endpoints ====================

@app.post("/api/chat", response_model=AgentResponse)
async def chat(message: ChatMessage):
    """
    Process a chat message through the agent system.
    """
    if not agents:
        raise HTTPException(status_code=503, detail="Agents not initialized")

    # Check guardrails
    if settings.security.enable_guardrails:
        check_result = guardrails.check_input(message.message)
        if not check_result.get("allowed"):
            return AgentResponse(
                success=False,
                message="Your message was blocked by security policies.",
                agent="guardrails",
                data={"violations": check_result.get("violations")}
            )

    try:
        # For now, we'll implement a simple response
        # In production, this would use the actual ADK agent
        response_text = f"Received: {message.message}"

        # Check if this is a data-related query
        lower_msg = message.message.lower()
        if "data" in lower_msg or "query" in lower_msg or "select" in lower_msg:
            tables = db_tool.get_tables()
            response_text = f"I can help with data analysis. Available tables: {', '.join(tables) if tables else 'None'}"
        elif "map" in lower_msg or "location" in lower_msg:
            response_text = "I can help create interactive maps. Please provide a database table with latitude and longitude columns."
        elif "knowledge" in lower_msg or "document" in lower_msg or "policy" in lower_msg:
            response_text = "I can search the knowledge base. Please specify what you're looking for."

        return AgentResponse(
            success=True,
            message=response_text,
            agent="nexus_root"
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        return AgentResponse(
            success=False,
            message=f"Error processing request: {str(e)}",
            agent="system"
        )


# ==================== WebSocket Endpoint ====================

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat.
    """
    await websocket.accept()
    session_id = None

    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)

            message = message_data.get("message", "")
            session_id = message_data.get("session_id")

            # Send acknowledgment
            await websocket.send_json({
                "type": "status",
                "status": "processing",
                "message": "Processing your request..."
            })

            # Check guardrails
            if settings.security.enable_guardrails:
                check = guardrails.check_input(message)
                if not check.get("allowed"):
                    await websocket.send_json({
                        "type": "error",
                        "message": "Message blocked by security policies"
                    })
                    continue

            # Process message (simplified for WebSocket)
            response = f"Echo: {message}"

            # Send response
            await websocket.send_json({
                "type": "response",
                "message": response,
                "timestamp": datetime.now().isoformat()
            })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })


# ==================== File Processing Endpoints ====================

@app.post("/api/files/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process a file.
    """
    try:
        # Read file content
        content = await file.read()

        # Process based on file type
        filename = file.filename
        ext = filename.split('.')[-1].lower() if '.' in filename else ''

        # Import base64 for encoding
        import base64

        if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp']:
            # Process image
            result = file_tool.process_image(content, filename)
            return FileUploadResponse(
                success=result.get("success", False),
                filename=filename,
                file_type="image",
                content=result
            )
        elif ext == 'pdf':
            # Process PDF
            result = file_tool.process_pdf(content, filename)
            return FileUploadResponse(
                success=result.get("success", False),
                filename=filename,
                file_type="pdf",
                content=result
            )
        elif ext in ['csv', 'txt', 'md']:
            # Process text/CSV
            result = file_tool.process_csv(content, filename)
            return FileUploadResponse(
                success=result.get("success", False),
                filename=filename,
                file_type="data",
                content=result
            )
        else:
            return FileUploadResponse(
                success=False,
                filename=filename,
                file_type="unknown",
                error=f"Unsupported file type: {ext}"
            )

    except Exception as e:
        logger.error(f"File upload error: {e}")
        return FileUploadResponse(
            success=False,
            filename=file.filename if file else "unknown",
            file_type="error",
            error=str(e)
        )


# ==================== Database Endpoints ====================

@app.get("/api/db/tables")
async def list_tables():
    """List all database tables."""
    try:
        tables = db_tool.get_tables()
        return {"success": True, "tables": tables}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/db/tables/{table_name}/schema")
async def get_table_schema(table_name: str):
    """Get table schema."""
    try:
        schema = db_tool.get_table_schema(table_name)
        return schema
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/api/db/tables/{table_name}/sample")
async def get_table_sample(table_name: str, limit: int = Query(10, ge=1, le=100)):
    """Get sample data from a table."""
    try:
        data = db_tool.get_sample_data(table_name, limit)
        return data
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/db/query")
async def execute_query(query: str):
    """Execute a SQL query."""
    try:
        # Check guardrails
        if settings.security.enable_guardrails:
            check = guardrails.check_sql_query(query)
            if not check.get("allowed"):
                return {
                    "success": False,
                    "error": check.get("reason", "Query blocked by security policies")
                }

        result = db_tool.execute_query(query)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== Knowledge Base Endpoints ====================

@app.get("/api/knowledge/collections")
async def list_collections():
    """List all knowledge base collections."""
    from backend.tools.rag import kb_tool
    try:
        collections = kb_tool.list_collections()
        return {
            "success": True,
            "collections": [{"name": c.name, "count": c.count()} for c in collections]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/knowledge/query")
async def query_knowledge(collection: str, query: str, n_results: int = 5):
    """Query the knowledge base."""
    from backend.tools.rag import kb_tool
    try:
        result = kb_tool.query(collection, query, n_results)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== Visualization Endpoints ====================

@app.post("/api/visualize/chart")
async def create_chart(
    query: Optional[str] = None,
    data: Optional[str] = None,
    chart_type: str = "bar",
    x: Optional[str] = None,
    y: Optional[str] = None,
    title: str = "Chart"
):
    """Create a chart from data."""
    from backend.tools.data_analysis import analysis_tool
    import pandas as pd

    try:
        if query:
            # Get data from database
            result = db_tool.execute_query(query)
            if not result.get("success"):
                return result
            df = pd.DataFrame(result["data"])
        elif data:
            # Use provided data
            df = pd.DataFrame(json.loads(data))
        else:
            return {"success": False, "error": "Either query or data must be provided"}

        # Create chart
        chart = analysis_tool.create_chart(df, chart_type, x, y, title)
        return chart
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/api/visualize/map")
async def create_map(
    query: Optional[str] = None,
    data: Optional[str] = None,
    lat_column: str = "lat",
    lon_column: str = "lon",
    popup_fields: Optional[str] = None,
    map_type: str = "openstreetmap"
):
    """Create a map from location data."""
    from backend.tools.maps import map_tool
    import pandas as pd

    try:
        if query:
            result = db_tool.execute_query(query)
            if not result.get("success"):
                return result
            data_list = result["data"]
        elif data:
            data_list = json.loads(data)
        else:
            return {"success": False, "error": "Either query or data must be provided"}

        # Create map
        popup_list = popup_fields.split(",") if popup_fields else None
        map_result = map_tool.create_map_from_data(
            data_list,
            lat_column=lat_column,
            lon_column=lon_column,
            popup_fields=popup_list,
            map_type=map_type
        )
        return map_result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==================== Static Files ====================

@app.get("/map-viewer")
async def map_viewer():
    """Map viewer page."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Map Viewer - Nexus ADK</title>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Inter', sans-serif; }
            #map { height: 100vh; width: 100%; }
            .title {
                position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
                z-index: 1000; background: white; padding: 10px 20px;
                border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            }
        </style>
    </head>
    <body>
        <div class="title"><h2>Interactive Map Viewer</h2></div>
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([40.7128, -74.0060], 10);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


# ==================== Main Entry Point ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
