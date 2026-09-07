"""
Voice + Document Service
------------------------

Điều phối pipeline:

    Voice transcript
        ↓
    DocumentRequest
        ↓
    generate_document()
        ↓
    AIService
        ↓
    DocumentBuilder
        ↓
    DocumentResponse
"""

from __future__ import annotations

from typing import Any

from app.schemas.document import (
    DocumentRequest,
    DocumentResponse,
)
from app.services.document_service import (
    generate_document,
)


class VoiceDocumentService:
    """
    Chuyển transcript từ Voice thành văn bản Word thông qua
    pipeline Document hiện có của hệ thống.
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def _validate_transcript(
        transcript: str,
    ) -> str:
        if not isinstance(transcript, str):
            raise TypeError(
                "transcript phải là chuỗi."
            )

        normalized = transcript.strip()

        if not normalized:
            raise ValueError(
                "transcript không được để trống."
            )

        return normalized

    @staticmethod
    def _validate_document_type(
        document_type: str,
    ) -> str:
        if not isinstance(document_type, str):
            raise TypeError(
                "document_type phải là chuỗi."
            )

        normalized = document_type.strip()

        if not normalized:
            raise ValueError(
                "document_type không được để trống."
            )

        return normalized

    @staticmethod
    def _validate_title(
        title: str,
    ) -> str:
        if not isinstance(title, str):
            raise TypeError(
                "title phải là chuỗi."
            )

        normalized = title.strip()

        if not normalized:
            raise ValueError(
                "title không được để trống."
            )

        return normalized

    @staticmethod
    def _validate_provider(
        provider: str,
    ) -> str:
        if provider not in {
            "ollama",
            "gemini",
            "openai",
        }:
            raise ValueError(
                "provider phải là một trong: "
                "ollama, gemini, openai."
            )

        return provider

    def process(
        self,
        *,
        transcript: str,
        document_type: str,
        title: str,
        provider: str = "ollama",
        metadata: dict[str, Any] | None = None,
    ) -> DocumentResponse:
        """
        Chuyển transcript thành văn bản Word.

        transcript:
            Nội dung được nhận diện từ audio.

        document_type:
            Loại văn bản theo hệ thống Document hiện tại.

        title:
            Tiêu đề văn bản.

        provider:
            AI provider hiện tại của Document pipeline.

        metadata:
            Metadata bổ sung từ Voice pipeline.
        """

        transcript = self._validate_transcript(
            transcript
        )

        document_type = self._validate_document_type(
            document_type
        )

        title = self._validate_title(
            title
        )

        provider = self._validate_provider(
            provider
        )

        request = DocumentRequest(
            provider=provider,
            type=document_type,
            title=title,
            prompt=transcript,
            content=transcript,
        )

        result = generate_document(
            request
        )

        return result
