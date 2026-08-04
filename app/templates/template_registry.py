"""
Template Registry
-----------------

Quản lý toàn bộ Word Template của hệ thống.
"""

from app.templates.template_definition import (
    TemplateDefinition,
)


class TemplateRegistry:
    """
    Quản lý danh sách TemplateDefinition.
    """

    _templates: dict[str, TemplateDefinition] = {}

    # =====================================================
    # REGISTER
    # =====================================================

    @classmethod
    def register(
        cls,
        definition: TemplateDefinition,
    ) -> None:
        """
        Đăng ký một Template.
        """

        cls._templates[
            definition.template_name
        ] = definition

    # =====================================================
    # GET
    # =====================================================

    @classmethod
    def get(
        cls,
        template_name: str,
    ) -> TemplateDefinition:
        """
        Lấy TemplateDefinition theo tên.
        """

        template = cls._templates.get(
            template_name
        )

        if template is None:

            raise ValueError(
                f"Không tìm thấy Template '{template_name}'."
            )

        return template

    # =====================================================
    # EXISTS
    # =====================================================

    @classmethod
    def exists(
        cls,
        template_name: str,
    ) -> bool:
        """
        Kiểm tra Template tồn tại.
        """

        return (
            template_name
            in cls._templates
        )

    # =====================================================
    # REMOVE
    # =====================================================

    @classmethod
    def unregister(
        cls,
        template_name: str,
    ) -> None:
        """
        Hủy đăng ký Template.
        """

        cls._templates.pop(
            template_name,
            None,
        )

    # =====================================================
    # ALL
    # =====================================================

    @classmethod
    def all(
        cls,
    ) -> list[TemplateDefinition]:
        """
        Trả về toàn bộ Template.
        """

        return list(
            cls._templates.values()
        )

    # =====================================================
    # CLEAR
    # =====================================================

    @classmethod
    def clear(
        cls,
    ) -> None:
        """
        Xóa toàn bộ Template.
        """

        cls._templates.clear()


# =====================================================
# DEFAULT TEMPLATES
# =====================================================

TemplateRegistry.register(
    TemplateDefinition(
        template_name="cong_van",
        display_name="Mẫu Công văn",
        description="Template công văn hành chính",
        file_name="cong_van.docx",
    )
)

TemplateRegistry.register(
    TemplateDefinition(
        template_name="ke_hoach",
        display_name="Mẫu Kế hoạch",
        description="Template kế hoạch",
        file_name="ke_hoach.docx",
    )
)

TemplateRegistry.register(
    TemplateDefinition(
        template_name="bao_cao",
        display_name="Mẫu Báo cáo",
        description="Template báo cáo",
        file_name="bao_cao.docx",
    )
)

TemplateRegistry.register(
    TemplateDefinition(
        template_name="thong_bao",
        display_name="Mẫu Thông báo",
        description="Template thông báo",
        file_name="thong_bao.docx",
    )
)

TemplateRegistry.register(
    TemplateDefinition(
        template_name="quyet_dinh",
        display_name="Mẫu Quyết định",
        description="Template quyết định",
        file_name="quyet_dinh.docx",
    )
)

TemplateRegistry.register(
    TemplateDefinition(
        template_name="to_trinh",
        display_name="Mẫu Tờ trình",
        description="Template tờ trình",
        file_name="to_trinh.docx",
    )
)

TemplateRegistry.register(
    TemplateDefinition(
        template_name="giay_moi",
        display_name="Mẫu Giấy mời",
        description="Template giấy mời",
        file_name="giay_moi.docx",
    )
)