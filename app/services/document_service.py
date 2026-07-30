from app.services.ai_service import AIService
from app.services.document_builder import DocumentBuilder


def generate_document(data):
    """
    Sinh văn bản hoàn chỉnh.

    Quy trình:
        1. Gọi AI sinh nội dung.
        2. Gán nội dung AI vào data.
        3. DocumentBuilder chọn template phù hợp.
        4. Sinh file Word.
        5. Trả thông tin tải xuống.
    """

    # =====================================================
    # AI
    # =====================================================

    ai = AIService()

    ai_content = ai.generate_document(
        document_type=data.type,
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

    result = builder.build(
        data,
    )

    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "success": result["success"],
        "file_name": result["file_name"],
        "download_url": (
            f"/document/download/{result['file_name']}"
        ),
    }