"""
Provider Factory
----------------

Factory tạo AI Provider theo cấu hình hệ thống.
"""

from app.core.config import AI_PROVIDER

from app.providers.base_provider import BaseProvider
from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider


class ProviderFactory:
    """
    Factory khởi tạo AI Provider theo cấu hình.
    """

    _providers = {
        "ollama": OllamaProvider,
        "openai": OpenAIProvider,

        # Gemini sử dụng OpenAI SDK
        "gemini": OpenAIProvider,
    }

    @classmethod
    def create(cls) -> BaseProvider:
        """
        Tạo Provider theo cấu hình AI_PROVIDER.
        """

        provider_name = AI_PROVIDER.lower().strip()

        provider_class = cls._providers.get(
            provider_name
        )

        if provider_class is None:

            supported = ", ".join(
                cls._providers.keys()
            )

            raise ValueError(
                f"Provider '{provider_name}' không được hỗ trợ.\n"
                f"Các Provider hiện có: {supported}"
            )

        return provider_class()