"""
Document Service
----------------

Điều phối toàn bộ quy trình sinh văn bản.
"""

from app.documents.document_factory import DocumentFactory
from app.services.ai_service import AIService
from app.services.document_builder import DocumentBuilder
from app.templates.template_factory import TemplateFactory
from app.templates.template_loader import TemplateLoader


def generate_document(data):
    """
    Sinh văn bản hoàn chỉnh.

    Quy trình:

        1. Xác định loại văn bản.
        2. Xác định template.
        3. Kiểm tra template tồn tại.
        4. AI sinh nội dung.
        5. Build Word.
        6. Trả kết quả.
    """

    # =====================================================
    # DOCUMENT
    # =====================================================

    document = DocumentFactory.create(data.type)

    # =====================================================
    # TEMPLATE
    # =====================================================

    template = TemplateFactory.create(
        document.template_name
    )

    loader = TemplateLoader()

    if not loader.exists(template.template_name):
        raise FileNotFoundError(
            f"Không tìm thấy template '{template.file_name}'."
        )

    # =====================================================
    # AI
    # =====================================================

    ai = AIService()

    ai_content = ai.generate_document(
        document_type=document.document_type,
        title=data.title,
        content=data.content,
    )

    # =====================================================
    # GÁN NỘI DUNG AI
    # =====================================================

    data.content = ai_content

    # =====================================================
    # BUILD DOCUMENT
    # =====================================================

    builder = DocumentBuilder()

    result = builder.build(data)

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "success": result["success"],
        "document_type": document.document_type,
        "document_name": document.display_name,
        "template_name": template.template_name,
        "file_name": result["file_name"],
        "download_url": (
            f"/document/download/{result['file_name']}"
        ),
    }