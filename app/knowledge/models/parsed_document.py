"""
Parsed Document Models
----------------------

Model dữ liệu trung gian sau khi Parser đọc tài liệu.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ParsedPage:
    """
    Nội dung của một trang tài liệu.
    """

    page_number: int
    text: str
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class ParsedDocument:
    """
    Kết quả chuẩn hóa từ Parser.
    """

    text: str

    source: str = ""

    pages: list[ParsedPage] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )