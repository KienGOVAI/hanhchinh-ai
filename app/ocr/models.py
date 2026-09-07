"""
OCR Domain Models
-----------------

Model dữ liệu trung gian cho kết quả OCR.

OCR Pipeline:

    PDF / Ảnh / Scan
            ↓
           OCR
            ↓
       OCRDocument
            ↓
      OCRPage / OCRBlock
            ↓
       Text chuẩn hóa
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class OCRBlock:
    """
    Một vùng nội dung được OCR nhận diện
    trong một trang tài liệu.
    """

    text: str

    confidence: float | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class OCRPage:
    """
    Kết quả OCR của một trang tài liệu.
    """

    page_number: int

    text: str

    confidence: float | None = None

    blocks: list[OCRBlock] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class OCRDocument:
    """
    Kết quả OCR chuẩn hóa của toàn bộ tài liệu.
    """

    text: str

    source: str = ""

    pages: list[OCRPage] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )