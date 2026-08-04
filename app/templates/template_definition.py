"""
Template Definition
-------------------

Định nghĩa metadata của một Word Template.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class TemplateDefinition:
    """
    Metadata của một Template.
    """

    # =====================================================
    # Thông tin cơ bản
    # =====================================================

    template_name: str

    display_name: str

    description: str

    # =====================================================
    # File
    # =====================================================

    file_name: str

    file_extension: str = ".docx"

    template_folder: str = "templates"

    # =====================================================
    # Trạng thái
    # =====================================================

    enabled: bool = True

    version: str = "1.0"

    author: str = "HanhChinhAI"

    # =====================================================
    # Khả năng của Template
    # =====================================================

    supports_header: bool = True

    supports_footer: bool = True

    supports_signature: bool = True

    supports_table: bool = False

    supports_image: bool = False

    supports_qrcode: bool = False

    supports_watermark: bool = False

    supports_pdf_export: bool = False

    # =====================================================
    # Placeholder
    # =====================================================

    placeholders: tuple[str, ...] = ()

    # =====================================================
    # Metadata
    # =====================================================

    tags: tuple[str, ...] = ()

    category: str = "administrative"

    metadata: dict[str, str] = field(
        default_factory=dict
    )