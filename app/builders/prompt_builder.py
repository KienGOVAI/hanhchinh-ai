"""
Prompt Builder
--------------

Ghép System Prompt + Document Prompt + Context + User Input.
"""

from app.documents.document_definition import DocumentDefinition
from app.services.prompt_loader import PromptLoader

class PromptBuilder:

    def __init__(self):

        self.loader = PromptLoader()

    def build(
        self,
        document: DocumentDefinition,
        user_input: str,
        context: str = ""
    ) -> str:

        # ==========================
        # Load System Prompt
        # ==========================

        system_prompt = self.loader.load(
            "system",
            "system"
        )

        # ==========================
        # Load Document Prompt
        # ==========================

        document_prompt = self.loader.load(
            document.prompt_category,
            document.prompt_name
        )

        # ==========================
        # Build Prompt
        # ==========================

        prompt = f"""{system_prompt}

{document_prompt}
"""

        if context:

            prompt += f"""

====================
CONTEXT
====================

{context}
"""

        prompt += f"""

====================
USER REQUEST
====================

{user_input}
"""

        return prompt.strip()