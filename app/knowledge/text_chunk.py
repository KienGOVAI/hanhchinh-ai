"""
Text Chunk
----------

Định nghĩa một đoạn văn bản sau khi được chia nhỏ.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class TextChunk:
    """
    Một đoạn văn bản phục vụ RAG.
    """

    # =====================================================
    # Định danh
    # =====================================================

    chunk_id: str

    knowledge_id: str

    # =====================================================
    # Nội dung
    # =====================================================

    text: str

    # =====================================================
    # Vị trí
    # =====================================================

    index: int

    start: int

    end: int

    # =====================================================
    # Metadata
    # =====================================================

    metadata: Dict = None

    # =====================================================
    # Helper
    # =====================================================

    @property
    def length(self) -> int:
        """
        Độ dài chunk.
        """
        return len(self.text)

    def to_dict(self):
        """
        Chuyển thành dictionary.
        """
        return {
            "chunk_id": self.chunk_id,
            "knowledge_id": self.knowledge_id,
            "text": self.text,
            "index": self.index,
            "start": self.start,
            "end": self.end,
            "length": self.length,
            "metadata": self.metadata or {},
        }