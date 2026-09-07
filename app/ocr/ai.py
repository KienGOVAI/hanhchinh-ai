"""
OCR + AI Service
----------------

Sprint 14.4 — OCR + AI

Pipeline:

    OCRDocument
        ↓
    OCR text
        ↓
    User instruction
        ↓
    AssistantService
        ↓
    AI answer
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.knowledge.assistant import (
    AssistantResponse,
    AssistantService,
)


class OCRAIServiceError(Exception):
    """Lỗi chung của OCR + AI Service."""


class InvalidOCRDocumentError(OCRAIServiceError):
    """OCRDocument không hợp lệ."""


class EmptyOCRTextError(OCRAIServiceError):
    """OCRDocument không có nội dung văn bản."""


class OCRAIInstructionError(OCRAIServiceError):
    """Yêu cầu xử lý AI không hợp lệ."""


@dataclass
class OCRAIResponse:
    """Kết quả xử lý OCR + AI."""

    answer: str
    ocr_text: str
    instruction: str
    metadata: dict[str, Any]


class OCRAIService:
    """
    Service kết nối OCR với Assistant.

    Trách nhiệm:
        1. Nhận OCRDocument.
        2. Lấy toàn bộ text OCR.
        3. Kiểm tra text.
        4. Chuẩn hóa yêu cầu người dùng.
        5. Chuyển nội dung OCR cho AssistantService.
        6. Trả kết quả AI.

    Service này KHÔNG trực tiếp gọi PaddleOCR.

    PaddleOCR:
        app.ocr.engine

    Assistant:
        app.knowledge.assistant
    """

    def __init__(self, assistant_service: AssistantService) -> None:
        if assistant_service is None:
            raise ValueError("assistant_service không được None.")

        self.assistant_service = assistant_service

    @staticmethod
    def _validate_document(document: Any) -> str:
        """Kiểm tra OCRDocument và lấy text."""

        if document is None:
            raise InvalidOCRDocumentError(
                "OCRDocument không được None."
            )

        text = getattr(document, "text", None)

        if not isinstance(text, str):
            raise InvalidOCRDocumentError(
                "OCRDocument phải có trường text kiểu str."
            )

        normalized_text = text.strip()

        if not normalized_text:
            raise EmptyOCRTextError(
                "OCRDocument không có nội dung văn bản."
            )

        return normalized_text

    @staticmethod
    def _validate_instruction(instruction: str) -> str:
        """Kiểm tra và chuẩn hóa yêu cầu AI."""

        if not isinstance(instruction, str):
            raise OCRAIInstructionError(
                "instruction phải là chuỗi."
            )

        normalized = instruction.strip()

        if not normalized:
            raise OCRAIInstructionError(
                "instruction không được để trống."
            )

        return normalized

    @staticmethod
    def _build_question(
        ocr_text: str,
        instruction: str,
    ) -> str:
        """Tạo câu hỏi gửi tới AssistantService."""

        return (
            "Bạn đang xử lý nội dung được trích xuất "
            "từ một tài liệu bằng OCR.\n\n"
            "NỘI DUNG OCR:\n"
            "--------------------\n"
            f"{ocr_text}\n"
            "--------------------\n\n"
            "YÊU CẦU CỦA NGƯỜI DÙNG:\n"
            f"{instruction}\n\n"
            "Hãy xử lý yêu cầu dựa trên nội dung OCR "
            "ở trên."
        )

    def process(
        self,
        document: Any,
        instruction: str,
    ) -> OCRAIResponse:
        """Xử lý OCRDocument → Assistant → kết quả AI."""

        ocr_text = self._validate_document(document)

        normalized_instruction = self._validate_instruction(
            instruction
        )

        question = self._build_question(
            ocr_text,
            normalized_instruction,
        )

        try:
            assistant_response = self.assistant_service.answer(
                question
            )
        except Exception as exc:
            raise OCRAIServiceError(
                "AssistantService xử lý OCR + AI thất bại."
            ) from exc

        if not isinstance(
            assistant_response,
            AssistantResponse,
        ):
            raise OCRAIServiceError(
                "AssistantService không trả về "
                "AssistantResponse hợp lệ."
            )

        answer = assistant_response.answer

        if not isinstance(answer, str):
            raise OCRAIServiceError(
                "AssistantResponse.answer phải là chuỗi."
            )

        metadata = dict(assistant_response.metadata)

        metadata.update(
            {
                "pipeline_stage": "ocr_ai",
                "ocr_text_length": len(ocr_text),
                "instruction_length": len(
                    normalized_instruction
                ),
                "assistant_query": assistant_response.query,
                "citation_count": len(
                    assistant_response.citations
                ),
            }
        )

        return OCRAIResponse(
            answer=answer,
            ocr_text=ocr_text,
            instruction=normalized_instruction,
            metadata=metadata,
        )


def create_ocr_ai_service(
    assistant_service: AssistantService,
) -> OCRAIService:
    """Factory tạo OCRAIService."""

    return OCRAIService(
        assistant_service=assistant_service
    )
