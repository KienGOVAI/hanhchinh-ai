from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

from app.schemas.document import DocumentRequest
from app.services.document_service import generate_document

router = APIRouter()


@router.post("/document/generate")
def create_document(request: DocumentRequest):
    return generate_document(request)


@router.get("/document/download/{filename}")
def download_document(filename: str):

    file_path = os.path.join("output", filename)

    if not os.path.exists(file_path):
        return {"success": False, "message": "Không tìm thấy file."}

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )