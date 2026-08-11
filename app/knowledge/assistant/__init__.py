"""
AI Assistant Layer.

Task 12.14 - Assistant Integration.
"""

from app.knowledge.assistant.assistant_service import (
    AssistantService,
    AssistantServiceError,
    AssistantEmbeddingError,
    AssistantRetrievalError,
    AssistantContextError,
    AssistantResponse,
    InvalidAssistantQuestionError,
)

__all__ = [
    "AssistantService",
    "AssistantServiceError",
    "AssistantEmbeddingError",
    "AssistantRetrievalError",
    "AssistantContextError",
    "AssistantResponse",
    "InvalidAssistantQuestionError",
]