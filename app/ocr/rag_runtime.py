"""
OCR + RAG Runtime
=================

Sprint 14.5 — OCR + RAG Runtime

Quản lý instance OCRRAGService dùng chung
AssistantService của application.
"""

from __future__ import annotations

from app.knowledge.assistant import AssistantService

from app.ocr.rag import (
    OCRRAGService,
    create_ocr_rag_service,
)


# ============================================================
# RUNTIME
# ============================================================

ocr_rag_service: OCRRAGService | None = None


def configure_ocr_rag_service(
    assistant_service: AssistantService,
) -> OCRRAGService:
    """
    Cấu hình OCRRAGService từ AssistantService
    đang chạy trong application.
    """

    global ocr_rag_service

    ocr_rag_service = create_ocr_rag_service(
        assistant_service=assistant_service,
    )

    return ocr_rag_service


def get_ocr_rag_service() -> OCRRAGService:
    """
    Lấy OCRRAGService hiện tại.

    Runtime phải được configure trước.
    """

    if ocr_rag_service is None:
        raise RuntimeError(
            "OCRRAGService chưa được configure."
        )

    return ocr_rag_service