"""
Knowledge Loader
----------------

Quản lý và định vị các nguồn tri thức.
Không chịu trách nhiệm đọc nội dung tài liệu.
"""

from pathlib import Path
from typing import List

from app.knowledge.knowledge_definition import KnowledgeDefinition
from app.knowledge.knowledge_factory import KnowledgeFactory


class KnowledgeLoader:
    """
    Loader quản lý các nguồn tri thức.
    """

    def __init__(self):
        self.root = Path("knowledge")

    def get_definition(
        self,
        knowledge_id: str
    ) -> KnowledgeDefinition:
        """
        Lấy metadata của nguồn tri thức.
        """
        return KnowledgeFactory.create(knowledge_id)

    def get_path(
        self,
        knowledge_id: str
    ) -> Path:
        """
        Trả về đường dẫn tuyệt đối của tài liệu.
        """

        definition = self.get_definition(
            knowledge_id
        )

        path = (
            self.root
            / definition.category
            / definition.file_name
        )

        return path.resolve()

    def exists(
        self,
        knowledge_id: str
    ) -> bool:
        """
        Kiểm tra file có tồn tại.
        """

        return self.get_path(
            knowledge_id
        ).exists()

    def list(self) -> List[KnowledgeDefinition]:
        """
        Danh sách toàn bộ nguồn tri thức.
        """

        return KnowledgeFactory.all()

    def list_enabled(self) -> List[KnowledgeDefinition]:
        """
        Danh sách nguồn tri thức đang hoạt động.
        """

        return KnowledgeFactory.enabled()

    def list_by_category(
        self,
        category: str
    ) -> List[KnowledgeDefinition]:
        """
        Danh sách theo nhóm.
        """

        return KnowledgeFactory.by_category(category)