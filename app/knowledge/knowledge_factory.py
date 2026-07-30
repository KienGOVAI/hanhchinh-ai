"""
Knowledge Factory
-----------------

Factory tạo và cung cấp KnowledgeDefinition.
"""

from typing import List

from app.knowledge.knowledge_definition import KnowledgeDefinition
from app.knowledge.knowledge_registry import KnowledgeRegistry


class KnowledgeFactory:
    """
    Factory làm việc với KnowledgeRegistry.
    """

    @staticmethod
    def create(knowledge_id: str) -> KnowledgeDefinition:
        """
        Lấy một KnowledgeDefinition theo ID.
        """
        return KnowledgeRegistry.get(knowledge_id)

    @staticmethod
    def exists(knowledge_id: str) -> bool:
        """
        Kiểm tra Knowledge có tồn tại.
        """
        return KnowledgeRegistry.exists(knowledge_id)

    @staticmethod
    def all() -> List[KnowledgeDefinition]:
        """
        Lấy toàn bộ Knowledge đã đăng ký.
        """
        return KnowledgeRegistry.list()

    @staticmethod
    def enabled() -> List[KnowledgeDefinition]:
        """
        Lấy các Knowledge đang được kích hoạt.
        """
        return KnowledgeRegistry.list_enabled()

    @staticmethod
    def by_category(category: str) -> List[KnowledgeDefinition]:
        """
        Lấy danh sách Knowledge theo nhóm.
        """
        return KnowledgeRegistry.list_by_category(category)