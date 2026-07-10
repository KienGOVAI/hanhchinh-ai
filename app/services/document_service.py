from pathlib import Path
from datetime import datetime

from app.templates.cong_van import CongVanTemplate
from app.services.ai_service import AIService

OUTPUT_DIR = Path("output")


def generate_document(data):

    OUTPUT_DIR.mkdir(exist_ok=True)

    # ==========================
    # Gọi AI
    # ==========================

    ai = AIService()

    ai_content = ai.generate_document(
        document_type=data.type,
        title=data.title,
        content=data.content
    )

    # ==========================
    # Gán nội dung AI sinh
    # ==========================

    data.content = ai_content

    # ==========================
    # Sinh Word
    # ==========================

    template = CongVanTemplate()

    doc = template.build(data)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    file_name = f"CongVan_{timestamp}.docx"

    file_path = OUTPUT_DIR / file_name

    doc.save(file_path)

    return {
        "success": True,
        "file_name": file_name,
        "download_url": f"/document/download/{file_name}"
    }