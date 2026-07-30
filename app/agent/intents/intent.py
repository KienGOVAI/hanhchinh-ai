"""
Intent Models
-------------
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Intent:
    """
    Intent được nhận diện từ yêu cầu người dùng.
    """

    name: str

    confidence: float

    entities: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
    DOCUMENT = "document"

RAG = "rag"

SEARCH = "search"

OCR = "ocr"

CHAT = "chat"

UNKNOWN = "unknown"