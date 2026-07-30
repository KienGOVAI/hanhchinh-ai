"""
RAG Service
-----------

Kết hợp Retrieval và AI để tạo câu trả lời có căn cứ.
"""

from app.knowledge.retriever import Retriever
from app.services.ai_service import AIService
from app.services.prompt_builder import PromptBuilder


class RAGService:

    def __init__(
        self,
        retriever: Retriever,
        ai_service: AIService,
        prompt_builder: PromptBuilder,
    ):

        self.retriever = retriever
        self.ai_service = ai_service
        self.prompt_builder = prompt_builder

    # =====================================================

    def answer(
        self,
        question: str,
        top_k: int = 5,
    ) -> str:
        """
        Trả lời câu hỏi dựa trên Knowledge Base.
        """

        retrieved = self.retriever.retrieve(
            query=question,
            top_k=top_k,
        )

        prompt = self.prompt_builder.build_rag_prompt(
            question=question,
            chunks=retrieved,
        )

        return self.ai_service.generate_text(
            prompt
        )