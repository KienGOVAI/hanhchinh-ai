from typing import Literal

from pydantic import BaseModel, Field, model_validator


class DocumentRequest(BaseModel):
    provider: Literal["ollama", "gemini", "openai"] = Field(
        default="ollama"
    )

    type: str = Field(...)

    title: str = Field(...)

    prompt: str = Field(...)

    # Template Engine sử dụng field này
    content: str = ""

    @model_validator(mode="after")
    def sync_content(self):
        if not self.content:
            self.content = self.prompt
        return self


class DocumentResponse(BaseModel):
    success: bool = True
    provider: str
    document_type: str
    file_name: str
    content: str
    message: str