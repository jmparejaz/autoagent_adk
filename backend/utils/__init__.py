"""
Utility functions for Nexus ADK Platform.
"""
import base64
import io
import json
import logging
import re
import hashlib
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def encode_image_to_base64(image_data: bytes) -> str:
    """Encode image bytes to base64 string."""
    return base64.b64encode(image_data).decode('utf-8')


def decode_base64_to_bytes(encoded: str) -> bytes:
    """Decode base64 string to bytes."""
    return base64.b64decode(encoded)


def sanitize_sql_query(query: str) -> str:
    """Sanitize SQL query to prevent injection."""
    # Remove potentially dangerous keywords
    dangerous_patterns = [
        r'\bDROP\b', r'\bDELETE\b', r'\bTRUNCATE\b',
        r'\bALTER\b', r'\bCREATE\s+TABLE\b', r'\bDROP\s+TABLE\b',
        r';--', r'/\*.*\*/', r'--.*$'
    ]

    sanitized = query
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)

    return sanitized.strip()


def is_safe_operation(operation: str, allowed_ops: List[str]) -> bool:
    """Check if SQL operation is allowed."""
    op_upper = operation.upper().strip()
    return op_upper in [op.upper() for op in allowed_ops]


def extract_table_names(query: str) -> List[str]:
    """Extract table names from SQL query."""
    pattern = r'\b(FROM|JOIN|INTO|UPDATE)\s+(\w+)'
    matches = re.findall(pattern, query, re.IGNORECASE)
    return [match[1] for match in matches]


def format_dataframe_to_json(df: pd.DataFrame, orient: str = 'records') -> str:
    """Format pandas DataFrame to JSON string."""
    return df.to_json(orient=orient, date_format='iso')


def json_to_dataframe(json_str: str) -> pd.DataFrame:
    """Convert JSON string to pandas DataFrame."""
    return pd.read_json(io.StringIO(json_str))


def calculate_data_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate summary statistics for DataFrame."""
    summary = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "null_counts": df.isnull().sum().to_dict(),
        "numeric_summary": {},
        "categorical_summary": {}
    }

    # Numeric columns summary
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        summary["numeric_summary"] = df[numeric_cols].describe().to_dict()

    # Categorical columns summary
    cat_cols = df.select_dtypes(include=['object', 'category']).columns
    if len(cat_cols) > 0:
        for col in cat_cols:
            summary["categorical_summary"][col] = {
                "unique_count": df[col].nunique(),
                "top_values": df[col].value_counts().head(5).to_dict()
            }

    return summary


def generate_session_id(user_id: str, timestamp: datetime) -> str:
    """Generate unique session ID."""
    data = f"{user_id}:{timestamp.isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def validate_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file type based on extension."""
    ext = filename.split('.')[-1].lower()
    return ext in [e.lower().lstrip('.') for e in allowed_extensions]


def extract_text_from_response(response: Any) -> str:
    """Extract text content from various response types."""
    if hasattr(response, 'text'):
        return response.text
    elif hasattr(response, 'content'):
        return response.content
    elif isinstance(response, dict):
        return json.dumps(response, indent=2)
    elif isinstance(response, str):
        return response
    return str(response)


def create_error_response(error: Exception, context: str = "") -> Dict[str, Any]:
    """Create standardized error response."""
    return {
        "error": type(error).__name__,
        "message": str(error),
        "context": context,
        "timestamp": datetime.now().isoformat()
    }


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks


def format_bytes_to_display(size_bytes: int) -> str:
    """Format bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"
