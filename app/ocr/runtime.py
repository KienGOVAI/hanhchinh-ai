"""
OCR Runtime
-----------

Sprint 14.4 — OCR + AI Runtime

Nhiệm vụ:

    AssistantService
        ↓
    OCRAIService

File này quản lý instance OCRAIService
dùng chung AssistantService của application.
"""

from __future__ import annotations

from app.knowledge.assistant import AssistantService

from app.ocr.ai import (
    OCRAIService,
    create_ocr_ai_service,
)


# ============================================================
# RUNTIME
# ============================================================

ocr_ai_service: OCRAIService | None = None


def configure_ocr_ai_service(
    assistant_service: AssistantService,
) -> OCRAIService:
    """
    Cấu hình OCRAIService từ AssistantService
    đang chạy trong application.
    """

    global ocr_ai_service

    ocr_ai_service = create_ocr_ai_service(
        assistant_service=assistant_service,
    )

    return ocr_ai_service


def get_ocr_ai_service() -> OCRAIService:
    """
    Lấy OCRAIService hiện tại.

    Runtime phải được configure trước khi gọi hàm này.
    """

    if ocr_ai_service is None:
        raise RuntimeError(
            "OCRAIService chưa được configure."
        )

    return ocr_ai_service
