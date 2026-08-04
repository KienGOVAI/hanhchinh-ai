from typing import Literal

from pydantic import BaseModel, Field


class GenerateDocumentRequest(BaseModel):
    """
    Request gửi từ Frontend tới Backend.
    """

    provider: Literal["ollama", "gemini", "openai"] = Field(
        default="ollama",
        description="AI Provider"
    )

    document_type: str = Field(
        ...,
        min_length=1,
        description="Loại văn bản"
    )

    title: str = Field(
        ...,
        min_length=1,
        description="Tiêu đề văn bản"
    )

    prompt: str = Field(
        ...,
        min_length=5,
        description="Nội dung yêu cầu AI"
    )


class GenerateDocumentResponse(BaseModel):
    """
    Kết quả trả về sau khi AI sinh văn bản.
    """

    provider: str

    content: str

    processing_time: float | None = None

    tokens: int | None = None