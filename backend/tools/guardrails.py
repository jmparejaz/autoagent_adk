"""
Guardrails and security tools for Nexus ADK Platform.
"""
import json
import logging
import re
from typing import Any, Dict, List, Optional, Set
from enum import Enum

from backend.config import settings

logger = logging.getLogger(__name__)


class GuardrailLevel(Enum):
    """Guardrail enforcement levels."""
    ALLOW = "allow"
    WARN = "warn"
    BLOCK = "block"


class GuardrailsTool:
    """Tool for enforcing security guardrails."""

    def __init__(self):
        self.config = settings.security
        self.enabled = self.config.enable_guardrails

        # Blocked patterns
        self.blocked_patterns = {
            "jailbreak": [
                r"ignore\s+(all\s+)?(rules?|instructions?|constraints?)",
                r"disregard\s+(all\s+)?(rules?|instructions?)",
                r"forget\s+(your\s+)?(instructions?|rules?|guidelines?)",
                r"new\s+instructions?",
                r"system\s*prompt\s*leak",
                r"you\s+are\s+(now\s+)?(a\s+)?(different|new)\s+(model|AI|assistant)",
                r"act\s+as\s+(a\s+)?(human|person|developer)",
                r"pretend\s+(to\s+)?(be|do)",
                r"do\s+anything\s+now",
                r" DAN\b",
            ],
            "harmful_content": [
                r"\b(hack|exploit|attack)\b.*\b(system|server|network)\b",
                r"create\s+(a\s+)?(virus|malware|ransomware)",
                r"how\s+to\s+(kill|hurt|harm|attack)",
                r"bomb\s+make",
                r"weapon\s+make",
            ],
            "pii": [
                r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
                r"\b\d{16}\b",  # Credit card
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            ]
        }

        # Allowed SQL operations
        self.allowed_operations = set(op.upper() for op in self.config.allowed_operations)

        # Dangerous SQL keywords
        self.dangerous_sql_keywords = [
            r"\bDROP\b", r"\bDELETE\b", r"\bTRUNCATE\b",
            r"\bALTER\b", r"\bCREATE\s+TABLE\b", r"\bDROP\s+TABLE\b",
            r"\bGRANT\b", r"\bREVOKE\b", r"\bOWNER\s+TO\b"
        ]

    def check_input(self, text: str) -> Dict[str, Any]:
        """
        Check input text against guardrails.

        Args:
            text: Input text to check

        Returns:
            Dictionary with check results
        """
        if not self.enabled:
            return {"allowed": True, "reason": "Guardrails disabled"}

        violations = []

        # Check blocked patterns
        for category, patterns in self.blocked_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    violations.append({
                        "category": category,
                        "pattern": pattern,
                        "matched": re.search(pattern, text, re.IGNORECASE).group()
                    })

        if violations:
            return {
                "allowed": False,
                "reason": "Input violates security policies",
                "violations": violations,
                "action": GuardrailLevel.BLOCK.value
            }

        return {"allowed": True, "reason": "Input passed all checks"}

    def check_sql_query(self, query: str) -> Dict[str, Any]:
        """
        Check SQL query for safety.

        Args:
            query: SQL query to check

        Returns:
            Dictionary with check results
        """
        if not self.enabled:
            return {"allowed": True, "reason": "Guardrails disabled"}

        query_upper = query.upper()

        # Check for dangerous operations
        for keyword in self.dangerous_sql_keywords:
            if re.search(keyword, query_upper):
                return {
                    "allowed": False,
                    "reason": f"Dangerous SQL operation detected: {keyword}",
                    "action": GuardrailLevel.BLOCK.value
                }

        # Extract operation type
        operation_match = re.match(r"^\s*(\w+)", query)
        if operation_match:
            operation = operation_match.group(1).upper()
            if operation not in self.allowed_operations:
                return {
                    "allowed": False,
                    "reason": f"Operation '{operation}' not allowed. Allowed: {self.allowed_operations}",
                    "action": GuardrailLevel.BLOCK.value
                }

        return {"allowed": True, "reason": "SQL query passed security checks"}

    def check_output(self, text: str) -> Dict[str, Any]:
        """
        Check output text for sensitive information leakage.

        Args:
            text: Output text to check

        Returns:
            Dictionary with check results
        """
        if not self.enabled:
            return {"allowed": True, "reason": "Guardrails disabled"}

        warnings = []

        # Check for potential PII in output
        for pattern_name, pattern in self.blocked_patterns.get("pii", {}).items():
            if re.search(pattern, text):
                warnings.append({
                    "category": "potential_pii",
                    "pattern": pattern_name
                })

        if warnings:
            return {
                "allowed": True,
                "warnings": warnings,
                "action": GuardrailLevel.WARN.value,
                "recommendation": "Review output for PII before presenting to user"
            }

        return {"allowed": True, "reason": "Output passed all checks"}

    def sanitize_response(self, response: str, max_length: int = 4000) -> str:
        """Sanitize response text."""
        # Truncate if too long
        if len(response) > max_length:
            response = response[:max_length] + "... [truncated]"

        return response


# Global guardrails tool instance
guardrails = GuardrailsTool()


def check_user_input(text: str) -> str:
    """
    ADK Tool: Check user input against guardrails.

    Args:
        text: Input text to check

    Returns:
        JSON string with check results
    """
    result = guardrails.check_input(text)
    return json.dumps(result)


def check_sql_safety(query: str) -> str:
    """
    ADK Tool: Check SQL query for safety.

    Args:
        query: SQL query to check

    Returns:
        JSON string with check results
    """
    result = guardrails.check_sql_query(query)
    return json.dumps(result)


def check_output_safety(text: str) -> str:
    """
    ADK Tool: Check output text for safety.

    Args:
        text: Output text to check

    Returns:
        JSON string with check results
    """
    result = guardrails.check_output(text)
    return json.dumps(result)


def sanitize_response_text(text: str, max_length: int = 4000) -> str:
    """
    ADK Tool: Sanitize response text.

    Args:
        text: Text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    return guardrails.sanitize_response(text, max_length)


def validate_operation(operation: str) -> str:
    """
    ADK Tool: Validate if an operation is allowed.

    Args:
        operation: Operation name to validate

    Returns:
        JSON string with validation result
    """
    operation_upper = operation.upper()
    allowed = operation_upper in guardrails.allowed_operations

    return json.dumps({
        "operation": operation,
        "allowed": allowed,
        "allowed_operations": list(guardrails.allowed_operations)
    })
