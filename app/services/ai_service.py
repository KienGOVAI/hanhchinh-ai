from app.services.prompt_builder import PromptBuilder
from app.providers.provider_factory import ProviderFactory


class AIService:

    def __init__(self):

        self.builder = PromptBuilder()

        self.provider = ProviderFactory.create()

    def generate_document(
        self,
        document_type,
        title,
        content
    ):

        prompt = self.builder.build(
            document_type,
            title,
            content
        )

        return self.provider.generate(prompt)