"""
OpenAI Provider
---------------

Provider sử dụng OpenAI API.
"""

from openai import OpenAI

from app.core.config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

from app.providers.base_provider import BaseProvider


class OpenAIProvider(BaseProvider):
    """
    AI Provider sử dụng OpenAI.
    """

    @property
    def provider_name(self) -> str:
        return "openai"

    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Sinh nội dung bằng OpenAI.

        Returns
        -------
        str
            Nội dung AI sinh ra.
        """

        if not OPENAI_API_KEY:
            raise RuntimeError(
                "OPENAI_API_KEY chưa được cấu hình."
            )

        try:

            client = OpenAI(
                api_key=OPENAI_API_KEY,
            )

            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.2,
            )

            content = (
                response.choices[0]
                .message
                .content
            )

            if content is None:
                raise RuntimeError(
                    "OpenAI không trả về nội dung."
                )

            content = content.strip()

            if not content:
                raise RuntimeError(
                    "OpenAI trả về nội dung rỗng."
                )

            return content

        except Exception as ex:
            raise RuntimeError(
                f"Lỗi OpenAI: {ex}"
            ) from ex