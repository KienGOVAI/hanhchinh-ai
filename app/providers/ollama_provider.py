"""
Ollama Provider
---------------

Provider sử dụng Ollama Local.
"""

import requests

from app.core.config import OLLAMA_MODEL
from app.providers.base_provider import BaseProvider


class OllamaProvider(BaseProvider):
    """
    AI Provider sử dụng Ollama Local.
    """

    BASE_URL = "http://localhost:11434/api/generate"

    @property
    def provider_name(self) -> str:
        return "ollama"

    def generate(
        self,
        prompt: str,
    ) -> str:
        """
        Sinh nội dung bằng Ollama.

        Returns
        -------
        str
            Nội dung AI sinh ra.
        """

        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        }

        try:
            response = requests.post(
                self.BASE_URL,
                json=payload,
                timeout=300,
            )

            response.raise_for_status()

            data = response.json()

            content = data.get("response", "").strip()

            if not content:
                raise RuntimeError(
                    "Ollama không trả về nội dung."
                )

            return content

        except requests.exceptions.RequestException as ex:
            raise RuntimeError(
                f"Không thể kết nối Ollama: {ex}"
            ) from ex

        except Exception as ex:
            raise RuntimeError(
                f"Lỗi Ollama: {ex}"
            ) from ex