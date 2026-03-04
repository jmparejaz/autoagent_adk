"""
Intent Classifier Agent - Routes user input to the appropriate workflow.
"""

import json
from typing import Optional
from backend.models.schemas import IntentClassification, WorkflowType


class IntentClassifier:
    """Classifies user intent and routes to appropriate workflow."""

    WORKFLOW_DESCRIPTIONS = {
        WorkflowType.DATA_ANALYSIS: "Data Analysis - For analyzing data, generating insights, creating charts, and running queries",
        WorkflowType.CODE_GEN: "Code Generation - For writing, reviewing, debugging, or explaining code",
        WorkflowType.RESEARCH: "Research - For searching information, summarizing content, and gathering facts",
        WorkflowType.GENERAL_CHAT: "General Chat - For casual conversation, general questions, and tasks that don't fit other categories"
    }

    def __init__(self, model=None):
        """Initialize the intent classifier."""
        self.model = model

    async def classify(self, user_message: str) -> IntentClassification:
        """
        Classify the user message and return the appropriate workflow.

        Args:
            user_message: The user's input message

        Returns:
            IntentClassification with workflow, confidence, and reasoning
        """
        if self.model:
            return await self._classify_with_llm(user_message)
        else:
            return self._classify_rule_based(user_message)

    async def _classify_with_llm(self, user_message: str) -> IntentClassification:
        """Use LLM to classify intent."""
        workflow_list = "\n".join([
            f"- {wf.value}: {desc}"
            for wf, desc in self.WORKFLOW_DESCRIPTIONS.items()
        ])

        prompt = f"""You are an intent classifier for an AI agent system.

Given the user's message below, classify it into the most appropriate workflow.

Available workflows:
{workflow_list}

User message: {user_message}

Return your classification in JSON format with the following structure:
{{
    "workflow": "workflow_name",
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation of why this workflow was chosen",
    "suggested_tools": ["tool1", "tool2"] (optional, if applicable)
}}

Only return the JSON, nothing else."""

        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text)

            workflow = WorkflowType(result.get("workflow", WorkflowType.GENERAL_CHAT.value))

            return IntentClassification(
                workflow=workflow,
                confidence=result.get("confidence", 0.8),
                reasoning=result.get("reasoning", "LLM classified intent"),
                suggested_tools=result.get("suggested_tools", [])
            )
        except Exception as e:
            print(f"Error in LLM classification: {e}")
            return self._classify_rule_based(user_message)

    def _classify_rule_based(self, user_message: str) -> IntentClassification:
        """Rule-based classification as fallback."""
        message_lower = user_message.lower()

        # Data analysis keywords
        data_keywords = ["analyze", "analysis", "data", "chart", "graph", "report", "statistics", "metrics", "insights", "trend"]
        if any(kw in message_lower for kw in data_keywords):
            return IntentClassification(
                workflow=WorkflowType.DATA_ANALYSIS,
                confidence=0.85,
                reasoning="Message contains data analysis keywords",
                suggested_tools=["data_query", "chart_generator"]
            )

        # Code generation keywords
        code_keywords = ["code", "program", "function", "class", "debug", "review", "write", "implement", "refactor", "algorithm"]
        if any(kw in message_lower for kw in code_keywords):
            return IntentClassification(
                workflow=WorkflowType.CODE_GEN,
                confidence=0.85,
                reasoning="Message contains code-related keywords",
                suggested_tools=["code_writer", "code_reviewer"]
            )

        # Research keywords
        research_keywords = ["search", "find", "research", "information", "what is", "how does", "explain", "describe", "tell me about"]
        if any(kw in message_lower for kw in research_keywords):
            return IntentClassification(
                workflow=WorkflowType.RESEARCH,
                confidence=0.8,
                reasoning="Message appears to be a research or information query",
                suggested_tools=["web_search", "content_summarizer"]
            )

        # Default to general chat
        return IntentClassification(
            workflow=WorkflowType.GENERAL_CHAT,
            confidence=0.6,
            reasoning="No specific workflow matched, defaulting to general chat",
            suggested_tools=[]
        )


# Global classifier instance
_classifier: Optional[IntentClassifier] = None


def get_intent_classifier(model=None) -> IntentClassifier:
    """Get the global intent classifier instance."""
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier(model)
    return _classifier
