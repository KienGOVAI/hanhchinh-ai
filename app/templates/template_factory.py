"""
Template Factory
----------------

Factory tạo và cung cấp TemplateDefinition.
"""

from app.templates.template_definition import (
    TemplateDefinition,
)
from app.templates.template_registry import (
    TemplateRegistry,
)


class TemplateFactory:
    """
    Factory làm việc với TemplateDefinition.
    """

    # =====================================================
    # CREATE
    # =====================================================

    @staticmethod
    def create(
        template_name: str,
    ) -> TemplateDefinition:
        """
        Lấy TemplateDefinition theo tên.
        """

        template = TemplateRegistry.get(
            template_name
        )

        if not template.enabled:
            raise ValueError(
                f"Template '{template_name}' đang bị vô hiệu hóa."
            )

        return template

    # =====================================================
    # EXISTS
    # =====================================================

    @staticmethod
    def exists(
        template_name: str,
    ) -> bool:
        """
        Kiểm tra Template tồn tại.
        """

        return TemplateRegistry.exists(
            template_name
        )

    # =====================================================
    # LIST
    # =====================================================

    @staticmethod
    def all(
        enabled_only: bool = False,
    ) -> list[TemplateDefinition]:
        """
        Trả về danh sách Template.
        """

        if enabled_only:
            return TemplateRegistry.enabled()

        return TemplateRegistry.list()

    # =====================================================
    # COUNT
    # =====================================================

    @staticmethod
    def count() -> int:
        """
        Tổng số Template.
        """

        return TemplateRegistry.count()