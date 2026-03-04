"""
Utility helpers for the agentic platform.
"""

import uuid
from datetime import datetime
from typing import Dict, Any


def generate_session_id() -> str:
    """Generate a unique session ID."""
    return f"session_{uuid.uuid4().hex[:12]}"


def generate_message_id() -> str:
    """Generate a unique message ID."""
    return f"msg_{uuid.uuid4().hex[:12]}"


def format_timestamp(dt: datetime = None) -> str:
    """Format a datetime object to ISO format."""
    if dt is None:
        dt = datetime.now()
    return dt.isoformat()


def sanitize_input(text: str) -> str:
    """Sanitize user input."""
    # Basic sanitization - remove potentially harmful content
    # In production, implement more robust sanitization
    return text.strip()


def create_error_response(error: str, code: int = 500) -> Dict[str, Any]:
    """Create a standardized error response."""
    return {
        "error": error,
        "code": code,
        "timestamp": format_timestamp()
    }
