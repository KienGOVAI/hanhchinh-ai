from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class OCRRAGResponseSchema(BaseModel):
    """
    API response cho Sprint 14.5 — OCR + RAG.
    """

    success: bool = True

    filename: str

    content_type: str | None = None

    file_size: int = Field(
        ...,
        ge=0,
    )

    ocr_text: str

    instruction: str

    answer: str

    sources: list[Any] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )