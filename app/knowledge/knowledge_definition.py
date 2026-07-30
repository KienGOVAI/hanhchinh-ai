"""
Knowledge Definition
--------------------

Định nghĩa metadata của một nguồn tri thức (Knowledge Source).
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KnowledgeDefinition:
    """
    Metadata của một nguồn tri thức.
    """

    # =====================================================
    # Thông tin cơ bản
    # =====================================================

    knowledge_id: str

    title: str

    description: str

    # =====================================================
    # Phân loại
    # =====================================================

    category: str

    source_type: str

    # =====================================================
    # File
    # =====================================================

    file_name: str

    file_extension: str

    knowledge_folder: str = "knowledge"

    # =====================================================
    # Metadata
    # =====================================================

    version: str = "1.0"

    author: str = "HanhChinhAI"

    language: str = "vi"

    enabled: bool = True

    # =====================================================
    # RAG
    # =====================================================

    chunk_size: int = 1000

    chunk_overlap: int = 200

    embedding_model: str = "BAAI/bge-m3"

    # =====================================================
    # Helper
    # =====================================================

    @property
    def full_path(self) -> Path:
        """
        Trả về đường dẫn đầy đủ tới file nguồn tri thức.
        """
        return (
            Path(self.knowledge_folder)
            / self.file_name
        )