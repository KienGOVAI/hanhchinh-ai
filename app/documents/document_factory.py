"""
Document Factory
----------------

Factory tạo và cung cấp thông tin DocumentDefinition.
"""

from app.documents.document_definition import DocumentDefinition
from app.documents.document_registry import DocumentRegistry


class DocumentFactory:
    """
    Factory tạo DocumentDefinition từ document_type.
    """

    @staticmethod
    def create(document_type: str) -> DocumentDefinition:
        """
        Trả về DocumentDefinition tương ứng.

        Args:
            document_type: Mã loại văn bản.

        Returns:
            DocumentDefinition
        """
        return DocumentRegistry.get(document_type)