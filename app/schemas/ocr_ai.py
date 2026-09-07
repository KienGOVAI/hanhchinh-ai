from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class OCRAIResponseSchema(BaseModel):
    """
    API response cho Sprint 14.4 — OCR + AI.
    """

    success: bool = True
    filename: str
    content_type: str | None = None
    file_size: int = Field(..., ge=0)

    ocr_text: str
    instruction: str
    answer: str

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )
