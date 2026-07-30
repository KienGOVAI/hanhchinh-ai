"""
Document Registry
-----------------

Quản lý các loại văn bản của hệ thống.
"""

from typing import Dict

from app.documents.document_definition import DocumentDefinition


class DocumentRegistry:

    _documents: Dict[str, DocumentDefinition] = {}

    @classmethod
    def register(cls, definition: DocumentDefinition):

        cls._documents[definition.document_type] = definition

    @classmethod
    def get(cls, document_type: str) -> DocumentDefinition:

        if document_type not in cls._documents:
            raise ValueError(
                f"Không tìm thấy Document '{document_type}'."
            )

        return cls._documents[document_type]

    @classmethod
    def exists(cls, document_type: str) -> bool:

        return document_type in cls._documents

    @classmethod
    def unregister(cls, document_type: str):

        cls._documents.pop(document_type, None)

    @classmethod
    def list(cls):

        return list(cls._documents.values())


# ===================================================
# Đăng ký các loại văn bản mặc định
# ===================================================

DocumentRegistry.register(
    DocumentDefinition(
        document_type="cong_van",
        display_name="Công văn",
        description="Soạn thảo công văn hành chính",
        prompt_category="document",
        prompt_name="cong_van",
        template_name="cong_van.docx",
        output_folder="CongVan",
        icon="📄"
    )
)

DocumentRegistry.register(
    DocumentDefinition(
        document_type="ke_hoach",
        display_name="Kế hoạch",
        description="Soạn thảo kế hoạch",
        prompt_category="document",
        prompt_name="ke_hoach",
        template_name="ke_hoach.docx",
        output_folder="KeHoach",
        icon="📝"
    )
)

DocumentRegistry.register(
    DocumentDefinition(
        document_type="bao_cao",
        display_name="Báo cáo",
        description="Soạn thảo báo cáo",
        prompt_category="document",
        prompt_name="bao_cao",
        template_name="bao_cao.docx",
        output_folder="BaoCao",
        icon="📊"
    )
)

DocumentRegistry.register(
    DocumentDefinition(
        document_type="thong_bao",
        display_name="Thông báo",
        description="Soạn thảo thông báo",
        prompt_category="document",
        prompt_name="thong_bao",
        template_name="thong_bao.docx",
        output_folder="ThongBao",
        icon="📢"
    )
)

DocumentRegistry.register(
    DocumentDefinition(
        document_type="quyet_dinh",
        display_name="Quyết định",
        description="Soạn thảo quyết định",
        prompt_category="document",
        prompt_name="quyet_dinh",
        template_name="quyet_dinh.docx",
        output_folder="QuyetDinh",
        icon="⚖️"
    )
)

DocumentRegistry.register(
    DocumentDefinition(
        document_type="giay_moi",
        display_name="Giấy mời",
        description="Soạn thảo giấy mời",
        prompt_category="document",
        prompt_name="giay_moi",
        template_name="giay_moi.docx",
        output_folder="GiayMoi",
        icon="✉️"
    )
)