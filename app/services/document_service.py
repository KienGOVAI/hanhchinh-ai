from pathlib import Path
from datetime import datetime

from app.templates.cong_van import CongVanTemplate

OUTPUT_DIR = Path("output")


def generate_document(data):

    OUTPUT_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    file_name = f"CongVan_{timestamp}.docx"

    file_path = OUTPUT_DIR / file_name

    # Khởi tạo Template
    template = CongVanTemplate()

    # Sinh văn bản
    doc = template.build(data)

    # Lưu
    doc.save(file_path)

    return {
        "success": True,
        "file_name": file_name,
        "download_url": f"/document/download/{file_name}"
    }