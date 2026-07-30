"""
Knowledge Registry
------------------

Quản lý toàn bộ nguồn tri thức của HanhChinhAI.
"""

from typing import Dict

from app.knowledge.knowledge_definition import KnowledgeDefinition


class KnowledgeRegistry:
    """
    Registry quản lý tất cả KnowledgeDefinition.
    """

    _knowledge: Dict[str, KnowledgeDefinition] = {}

    @classmethod
    def register(cls, definition: KnowledgeDefinition):
        """
        Đăng ký một nguồn tri thức.
        """
        cls._knowledge[definition.knowledge_id] = definition

    @classmethod
    def get(cls, knowledge_id: str) -> KnowledgeDefinition:
        """
        Lấy KnowledgeDefinition theo ID.
        """
        if knowledge_id not in cls._knowledge:
            raise ValueError(
                f"Knowledge '{knowledge_id}' không tồn tại."
            )

        return cls._knowledge[knowledge_id]

    @classmethod
    def exists(cls, knowledge_id: str) -> bool:
        """
        Kiểm tra nguồn tri thức đã được đăng ký.
        """
        return knowledge_id in cls._knowledge

    @classmethod
    def unregister(cls, knowledge_id: str):
        """
        Xóa một nguồn tri thức.
        """
        cls._knowledge.pop(knowledge_id, None)

    @classmethod
    def list(cls):
        """
        Danh sách toàn bộ KnowledgeDefinition.
        """
        return list(cls._knowledge.values())

    @classmethod
    def list_enabled(cls):
        """
        Danh sách các nguồn tri thức đang được kích hoạt.
        """
        return [
            knowledge
            for knowledge in cls._knowledge.values()
            if knowledge.enabled
        ]

    @classmethod
    def list_by_category(cls, category: str):
        """
        Lấy danh sách theo nhóm.
        """
        return [
            knowledge
            for knowledge in cls._knowledge.values()
            if knowledge.category == category
        ]


# =====================================================
# Knowledge Sources
# =====================================================

KnowledgeRegistry.register(
    KnowledgeDefinition(
        knowledge_id="luat_to_chuc_chinh_quyen_dia_phuong",

        title="Luật Tổ chức chính quyền địa phương",

        description="Nguồn tri thức về tổ chức chính quyền địa phương",

        category="law",

        source_type="pdf",

        file_name="luat_to_chuc_chinh_quyen_dia_phuong.pdf",

        file_extension=".pdf",
    )
)

KnowledgeRegistry.register(
    KnowledgeDefinition(
        knowledge_id="nghi_dinh_151_2025",

        title="Nghị định 151/2025/NĐ-CP",

        description="Nguồn tri thức Nghị định 151/2025/NĐ-CP",

        category="decree",

        source_type="pdf",

        file_name="nghi_dinh_151_2025.pdf",

        file_extension=".pdf",
    )
)

KnowledgeRegistry.register(
    KnowledgeDefinition(
        knowledge_id="thong_tu_01_2025",

        title="Thông tư 01/2025",

        description="Nguồn tri thức Thông tư 01/2025",

        category="circular",

        source_type="pdf",

        file_name="thong_tu_01_2025.pdf",

        file_extension=".pdf",
    )
)

KnowledgeRegistry.register(
    KnowledgeDefinition(
        knowledge_id="faq_hanh_chinh",

        title="FAQ Hành Chính",

        description="Các câu hỏi thường gặp",

        category="faq",

        source_type="md",

        file_name="faq.md",

        file_extension=".md",
    )
)