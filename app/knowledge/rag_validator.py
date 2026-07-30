"""
RAG Validator
-------------

Kiểm thử toàn bộ hệ thống RAG.
"""

from dataclasses import dataclass
from typing import List
import time

from app.services.rag_service import RAGService


@dataclass
class ValidationResult:

    question: str

    answer: str

    citation_count: int

    elapsed_seconds: float

    success: bool

    message: str


class RAGValidator:

    def __init__(
        self,
        rag_service: RAGService,
    ):

        self.rag_service = rag_service

    # =====================================================

    def validate_question(
        self,
        question: str,
    ) -> ValidationResult:

        start = time.perf_counter()

        try:

            response = self.rag_service.answer(
                question
            )

            elapsed = time.perf_counter() - start

            citation_count = 0

            if "Nguồn" in response:
                citation_count = response.count("[")

            return ValidationResult(

                question=question,

                answer=response,

                citation_count=citation_count,

                elapsed_seconds=elapsed,

                success=True,

                message="OK",
            )

        except Exception as ex:

            elapsed = time.perf_counter() - start

            return ValidationResult(

                question=question,

                answer="",

                citation_count=0,

                elapsed_seconds=elapsed,

                success=False,

                message=str(ex),
            )

    # =====================================================

    def validate(
        self,
        questions: List[str],
    ) -> List[ValidationResult]:

        return [
            self.validate_question(q)
            for q in questions
        ]