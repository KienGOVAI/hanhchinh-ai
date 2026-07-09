from app.schemas.document import (
    DocumentRequest,
    DocumentResponse,
)


class DocumentService:

    def generate(
        self,
        request: DocumentRequest
    ) -> DocumentResponse:

        return DocumentResponse(
            success=True,
            document_type=request.type,
            file_name="CongVan.docx",
            message="Đã tạo văn bản thành công."
        )