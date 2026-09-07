from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class VoiceUploadResponse(BaseModel):
    success: bool = True
    file_name: str
    text: str
    language: str = "vi"
    confidence: float | None = None
    duration: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    message: str = "Voice xử lý thành công."