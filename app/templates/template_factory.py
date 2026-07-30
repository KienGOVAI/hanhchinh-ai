"""
Template Factory
----------------

Factory tạo và cung cấp thông tin TemplateDefinition.
"""

from app.templates.template_definition import TemplateDefinition
from app.templates.template_registry import TemplateRegistry


class TemplateFactory:
    """
    Factory tạo TemplateDefinition từ template_name.
    """

    @staticmethod
    def create(template_name: str) -> TemplateDefinition:
        """
        Trả về TemplateDefinition tương ứng.

        Args:
            template_name: Tên template.

        Returns:
            TemplateDefinition
        """
        return TemplateRegistry.get(template_name)

    @staticmethod
    def exists(template_name: str) -> bool:
        """
        Kiểm tra template có tồn tại hay không.
        """
        return TemplateRegistry.exists(template_name)

    @staticmethod
    def all() -> list[TemplateDefinition]:
        """
        Trả về toàn bộ template đã đăng ký.
        """
        return TemplateRegistry.list()