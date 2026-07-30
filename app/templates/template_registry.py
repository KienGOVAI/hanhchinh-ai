"""
Template Registry
-----------------

Quản lý toàn bộ Word Template của hệ thống.
"""

from typing import Dict

from app.templates.template_definition import TemplateDefinition


class TemplateRegistry:
    """
    Quản lý danh sách TemplateDefinition.
    """

    _templates: Dict[str, TemplateDefinition] = {}

    @classmethod
    def register(cls, definition: TemplateDefinition):
        """
        Đăng ký một template.
        """
        cls._templates[definition.template_name] = definition

    @classmethod
    def get(cls, template_name: str) -> TemplateDefinition:
        """
        Lấy TemplateDefinition theo tên.
        """
        if template_name not in cls._templates:
            raise ValueError(
                f"Không tìm thấy Template '{template_name}'."
            )

        return cls._templates[template_name]

    @classmethod
    def exists(cls, template_name: str) -> bool:
        """
        Kiểm tra template có tồn tại không.
        """
        return template_name in cls._templates

    @classmethod
    def unregister(cls, template_name: str):
        """
        Hủy đăng ký template.
        """
        cls._templates.pop(template_name, None)

    @classmethod
    def list(cls):
        """
        Trả về danh sách tất cả template.
        """
        return list(cls._templates.values())


# ===================================================
# Đăng ký Template mặc định
# ===================================================

TemplateRegistry.register(
    TemplateDefinition(
        template_name="cong_van",
        display_name="Mẫu Công văn",
        description="Template công văn hành chính",
        file_name="cong_van.docx"
    )
)

TemplateRegistry.register(
    TemplateDefinition(
        template_name="ke_hoach",
        display_name="Mẫu Kế hoạch",
        description="Template kế hoạch",
        file_name="ke_hoach.docx"
    )
)

TemplateRegistry.register(
    TemplateDefinition(
        template_name="bao_cao",
        display_name="Mẫu Báo cáo",
        description="Template báo cáo",
        file_name="bao_cao.docx"
    )
)

TemplateRegistry.register(
    TemplateDefinition(
        template_name="thong_bao",
        display_name="Mẫu Thông báo",
        description="Template thông báo",
        file_name="thong_bao.docx"
    )
)

TemplateRegistry.register(
    TemplateDefinition(
        template_name="quyet_dinh",
        display_name="Mẫu Quyết định",
        description="Template quyết định",
        file_name="quyet_dinh.docx"
    )
)

TemplateRegistry.register(
    TemplateDefinition(
        template_name="giay_moi",
        display_name="Mẫu Giấy mời",
        description="Template giấy mời",
        file_name="giay_moi.docx"
    )
)