from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class VoiceAIResponse(BaseModel):
    success: bool = True
    file_name: str
    transcript: str
    answer: str
    language: str = "vi"
    duration: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    message: str = "Voice + AI xử lý thành công."