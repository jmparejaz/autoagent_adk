"""
Nexus ADK Platform Backend
===========================

A multimodal and multicapability agentic system using Google ADK.

Features:
- Process attached files (PDF, images)
- Connect to PostgreSQL databases for data analysis
- Generate interactive visualizations and maps
- RAG-based knowledge base for company documents
- Guardrails for security

Usage:
------
    from backend.agents import initialize_agents
    from backend.tools import db_tool, file_tool
    from backend.setup import setup

    # Initialize agents
    agents = initialize_agents()

    # Or use setup to register custom components
    setup.initialize()
"""

from backend.config import settings
from backend.tools.registry import registry
from backend.setup import setup

__version__ = "1.0.0"
__all__ = [
    "settings",
    "registry",
    "setup"
]
