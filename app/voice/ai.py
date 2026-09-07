from __future__ import annotations

from typing import Any

from app.api.schemas.assistant import AssistantResponseSchema
from app.knowledge.assistant.assistant_service import AssistantService


class VoiceAIService:
    """Xử lý transcript từ Voice bằng AI Assistant."""

    def __init__(self, assistant_service: AssistantService) -> None:
        if assistant_service is None:
            raise ValueError("assistant_service không được để trống.")

        self.assistant_service = assistant_service

    def process(
        self,
        transcript: str,
        metadata: dict[str, Any] | None = None,
    ) -> AssistantResponseSchema:
        """Gửi transcript tới AssistantService để AI xử lý."""

        if not isinstance(transcript, str):
            raise TypeError("transcript phải là chuỗi.")

        transcript = transcript.strip()

        if not transcript:
            raise ValueError("transcript không được để trống.")

        response = self.assistant_service.answer(transcript)

        return response