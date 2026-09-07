"""
OCR API Schemas
---------------

Pydantic schemas cho OCR API.

Sprint 14.3.5:
    - Chuẩn hóa OCR API response.
    - Chuyển OCRDocument thành JSON response.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class OCRBlockResponse(BaseModel):
    """Một block OCR trong một trang."""

    text: str = Field(
        ...,
        description="Nội dung văn bản được OCR.",
    )

    confidence: float | None = Field(
        default=None,
        description="Độ tin cậy OCR.",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata của block OCR.",
    )


class OCRPageResponse(BaseModel):
    """Kết quả OCR của một trang."""

    page_number: int = Field(
        ...,
        ge=1,
        description="Số thứ tự trang.",
    )

    text: str = Field(
        ...,
        description="Nội dung OCR của trang.",
    )

    confidence: float | None = Field(
        default=None,
        description="Độ tin cậy OCR của trang.",
    )

    blocks: list[OCRBlockResponse] = Field(
        default_factory=list,
        description="Danh sách block OCR của trang.",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata của trang.",
    )


class OCRUploadResponse(BaseModel):
    """
    Response chuẩn sau khi upload và thực hiện OCR.
    """

    success: bool = True

    filename: str = Field(
        ...,
        description="Tên file gốc được upload.",
    )

    content_type: str | None = Field(
        default=None,
        description="MIME type của file.",
    )

    file_size: int = Field(
        ...,
        ge=0,
        description="Kích thước file tính bằng byte.",
    )

    file_path: str = Field(
        ...,
        description="Đường dẫn file tạm đã lưu.",
    )

    text: str = Field(
        ...,
        description="Toàn bộ nội dung văn bản được OCR.",
    )

    pages: list[OCRPageResponse] = Field(
        default_factory=list,
        description="Danh sách kết quả OCR theo từng trang.",
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata của kết quả OCR.",
    )