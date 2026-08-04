import requests

from app.core.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
)

from app.providers.base_provider import BaseProvider
from app.schemas.document import DocumentResponse


class OpenRouterProvider(BaseProvider):
    """
    AI Provider sử dụng OpenRouter.
    """

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    @property
    def provider_name(self) -> str:
        return "openrouter"

    def generate(
        self,
        prompt: str,
    ) -> DocumentResponse:

        if not OPENROUTER_API_KEY:
            return DocumentResponse(
                success=False,
                provider=self.provider_name,
                document_type="unknown",
                file_name="",
                content="",
                message="Thiếu OPENROUTER_API_KEY trong file .env",
            )

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Hanh Chinh AI",
        }

        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }

        try:

            response = requests.post(
                self.BASE_URL,
                headers=headers,
                json=payload,
                timeout=120,
            )

            response.raise_for_status()

            data = response.json()

            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )

            return DocumentResponse(
                success=True,
                provider=self.provider_name,
                document_type="unknown",
                file_name="",
                content=content,
                message="Sinh văn bản thành công.",
            )

        except Exception as ex:

            return DocumentResponse(
                success=False,
                provider=self.provider_name,
                document_type="unknown",
                file_name="",
                content="",
                message=f"Lỗi OpenRouter: {ex}",
            )