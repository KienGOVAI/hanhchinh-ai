"""
OCR + RAG Service
=================

Sprint 14.5 — OCR + RAG

Pipeline:

    OCRDocument
        ↓
    OCR text
        ↓
    RAG / AssistantService
        ↓
    Knowledge Base
        ↓
    Context + Sources
        ↓
    AI Answer
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.knowledge.assistant import (
    AssistantResponse,
    AssistantService,
)


class OCRRAGServiceError(Exception):
    """Lỗi chung của OCR + RAG Service."""


class InvalidOCRRAGDocumentError(OCRRAGServiceError):
    """OCRDocument không hợp lệ."""


class EmptyOCRRAGTextError(OCRRAGServiceError):
    """OCRDocument không có nội dung."""


class OCRRAGInstructionError(OCRRAGServiceError):
    """Yêu cầu xử lý RAG không hợp lệ."""


@dataclass
class OCRRAGResponse:
    """Kết quả OCR + RAG."""

    answer: str
    ocr_text: str
    instruction: str
    sources: list[Any]
    metadata: dict[str, Any]


class OCRRAGService:
    """
    Service kết nối OCR với RAG hiện có.

    Trách nhiệm:

        1. Nhận OCRDocument.
        2. Lấy text OCR.
        3. Kiểm tra nội dung.
        4. Chuẩn hóa instruction.
        5. Tạo câu hỏi có nội dung OCR.
        6. Gửi sang AssistantService.
        7. Trả answer + sources + metadata.

    Không trực tiếp gọi PaddleOCR.

    Không tự triển khai Retriever/RAG mới.
    """

    def __init__(
        self,
        assistant_service: AssistantService,
    ) -> None:
        if assistant_service is None:
            raise ValueError(
                "assistant_service không được None."
            )

        self.assistant_service = assistant_service

    @staticmethod
    def _validate_document(
        document: Any,
    ) -> str:
        """Kiểm tra OCRDocument và lấy text."""

        if document is None:
            raise InvalidOCRRAGDocumentError(
                "OCRDocument không được None."
            )

        text = getattr(
            document,
            "text",
            None,
        )

        if not isinstance(text, str):
            raise InvalidOCRRAGDocumentError(
                "OCRDocument phải có trường text kiểu str."
            )

        normalized_text = text.strip()

        if not normalized_text:
            raise EmptyOCRRAGTextError(
                "OCRDocument không có nội dung văn bản."
            )

        return normalized_text

    @staticmethod
    def _validate_instruction(
        instruction: str,
    ) -> str:
        """Kiểm tra và chuẩn hóa yêu cầu."""

        if not isinstance(instruction, str):
            raise OCRRAGInstructionError(
                "instruction phải là chuỗi."
            )

        normalized = instruction.strip()

        if not normalized:
            raise OCRRAGInstructionError(
                "instruction không được để trống."
            )

        return normalized

    @staticmethod
    def _build_question(
        ocr_text: str,
        instruction: str,
    ) -> str:
        """
        Tạo câu hỏi gửi vào AssistantService.

        AssistantService hiện tại đã có RAG pipeline,
        vì vậy OCR text được đưa vào cùng instruction.
        """

        return (
            "Bạn đang xử lý nội dung được trích xuất "
            "từ một tài liệu bằng OCR.\n\n"
            "NỘI DUNG OCR:\n"
            "====================\n"
            f"{ocr_text}\n"
            "====================\n\n"
            "YÊU CẦU CỦA NGƯỜI DÙNG:\n"
            f"{instruction}\n\n"
            "Hãy sử dụng Knowledge Base và RAG hiện có "
            "để tìm các căn cứ liên quan nếu có. "
            "Sau đó trả lời dựa trên nội dung OCR "
            "và các căn cứ tìm được."
        )

    def process(
        self,
        document: Any,
        instruction: str,
    ) -> OCRRAGResponse:
        """
        OCRDocument → RAG → Answer + Sources.
        """

        ocr_text = self._validate_document(
            document
        )

        normalized_instruction = (
            self._validate_instruction(
                instruction
            )
        )

        question = self._build_question(
            ocr_text,
            normalized_instruction,
        )

        try:
            assistant_response = (
                self.assistant_service.answer(
                    question
                )
            )

        except Exception as exc:
            raise OCRRAGServiceError(
                "AssistantService xử lý OCR + RAG thất bại."
            ) from exc

        if not isinstance(
            assistant_response,
            AssistantResponse,
        ):
            raise OCRRAGServiceError(
                "AssistantService không trả về "
                "AssistantResponse hợp lệ."
            )

        answer = assistant_response.answer

        if not isinstance(answer, str):
            raise OCRRAGServiceError(
                "AssistantResponse.answer phải là chuỗi."
            )

        sources = list(
            assistant_response.citations
        )

        metadata = dict(
            assistant_response.metadata
        )

        metadata.update(
            {
                "pipeline_stage": "ocr_rag",
                "ocr_text_length": len(
                    ocr_text
                ),
                "instruction_length": len(
                    normalized_instruction
                ),
                "assistant_query": (
                    assistant_response.query
                ),
                "source_count": len(
                    sources
                ),
            }
        )

        return OCRRAGResponse(
            answer=answer,
            ocr_text=ocr_text,
            instruction=normalized_instruction,
            sources=sources,
            metadata=metadata,
        )


def create_ocr_rag_service(
    assistant_service: AssistantService,
) -> OCRRAGService:
    """Factory tạo OCRRAGService."""

    return OCRRAGService(
        assistant_service=assistant_service,
    )