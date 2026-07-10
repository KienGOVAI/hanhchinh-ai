from app.core.config import AI_PROVIDER

from app.providers.ollama_provider import OllamaProvider
from app.providers.openai_provider import OpenAIProvider


class ProviderFactory:

    @staticmethod
    def create():

        provider = AI_PROVIDER.lower()

        if provider == "ollama":
            return OllamaProvider()

        if provider == "gemini":
            return OpenAIProvider()

        raise Exception(
            f"Không hỗ trợ Provider: {provider}"
        )