from fastapi import APIRouter

from app.schemas.document import (
    DocumentRequest,
)

from app.services.document_service import (
    DocumentService,
)

router = APIRouter()

service = DocumentService()


@router.post("/document/generate")
def generate_document(request: DocumentRequest):

    return service.generate(request)