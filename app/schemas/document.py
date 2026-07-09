from pydantic import BaseModel


class DocumentRequest(BaseModel):
    type: str
    title: str
    content: str


class DocumentResponse(BaseModel):
    success: bool
    document_type: str
    file_name: str
    message: str