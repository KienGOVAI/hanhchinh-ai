"""Schemas cho Assistant API - Sprint 13.3."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field

class AssistantRequest(BaseModel):
    """Request gửi câu hỏi tới AI Assistant."""
    question: str = Field(..., min_length=1, description="Câu hỏi gửi tới AI Assistant.")
    conversation_id: str | None = Field(default=None, description="ID phiên hội thoại.")

class AssistantCitation(BaseModel):
    """Citation trả về cho client."""
    citation_id: str
    source: str
    score: float
    document_id: str | None = None
    page_number: int | None = None
    chunk_index: int | None = None
    content: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    label: str = ""

class AssistantResponseSchema(BaseModel):
    """Response của Assistant API."""
    success: bool = True
    question: str
    answer: str
    citations: list[AssistantCitation] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    message: str = "Assistant xử lý câu hỏi thành công."
