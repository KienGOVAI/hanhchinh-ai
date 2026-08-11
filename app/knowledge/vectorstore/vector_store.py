"""
Vector Store
------------

Lớp abstraction và Local Vector Store cho Knowledge Base.

Task 12.7:
- Lưu vector và metadata.
- Tìm kiếm similarity.
- Xóa vector theo document.
- Không phụ thuộc vào một vector database cụ thể.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any


# =========================================================
# EXCEPTIONS
# =========================================================


class VectorStoreError(Exception):
    """Lỗi chung của Vector Store."""


class VectorDimensionError(VectorStoreError):
    """Vector không đúng số chiều."""


class VectorNotFoundError(VectorStoreError):
    """Không tìm thấy vector."""


# =========================================================
# DATA MODEL
# =========================================================


@dataclass
class VectorRecord:
    """
    Một vector cùng metadata của nó.
    """

    vector_id: str

    vector: list[float]

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass
class VectorSearchResult:
    """
    Kết quả similarity search.
    """

    vector_id: str

    score: float

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


# =========================================================
# BASE VECTOR STORE
# =========================================================


class BaseVectorStore:
    """
    Interface chung cho Vector Store.
    """

    def add(
        self,
        record: VectorRecord,
    ) -> None:
        raise NotImplementedError

    def add_many(
        self,
        records: list[VectorRecord],
    ) -> None:
        raise NotImplementedError

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[VectorSearchResult]:
        raise NotImplementedError

    def delete(
        self,
        vector_id: str,
    ) -> None:
        raise NotImplementedError

    def delete_by_document(
        self,
        document_id: str,
    ) -> int:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def count(self) -> int:
        raise NotImplementedError


# =========================================================
# LOCAL VECTOR STORE
# =========================================================


class LocalVectorStore(BaseVectorStore):
    """
    Vector Store chạy local bằng Python.

    Phiên bản Sprint 12.7 dùng memory,
    mục đích là hoàn thiện abstraction và
    kiểm thử Retrieval trước khi tích hợp
    Vector Database thật.
    """

    def __init__(
        self,
        dimension: int | None = None,
    ) -> None:

        if dimension is not None and dimension <= 0:
            raise ValueError(
                "dimension phải lớn hơn 0."
            )

        self.dimension = dimension

        self._records: dict[
            str,
            VectorRecord,
        ] = {}

    # =====================================================
    # ADD
    # =====================================================

    def add(
        self,
        record: VectorRecord,
    ) -> None:

        self._validate_vector(
            record.vector
        )

        self._records[
            record.vector_id
        ] = record

    # =====================================================
    # ADD MANY
    # =====================================================

    def add_many(
        self,
        records: list[VectorRecord],
    ) -> None:

        for record in records:
            self.add(record)

    # =====================================================
    # SEARCH
    # =====================================================

    def search(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[VectorSearchResult]:

        if not query_vector:
            raise VectorStoreError(
                "query_vector không được rỗng."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k phải lớn hơn 0."
            )

        self._validate_vector(
            query_vector
        )

        results: list[
            VectorSearchResult
        ] = []

        for record in self._records.values():

            score = self._cosine_similarity(
                query_vector,
                record.vector,
            )

            results.append(
                VectorSearchResult(
                    vector_id=record.vector_id,
                    score=score,
                    metadata=dict(
                        record.metadata
                    ),
                )
            )

        results.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return results[:top_k]

    # =====================================================
    # DELETE
    # =====================================================

    def delete(
        self,
        vector_id: str,
    ) -> None:

        if vector_id not in self._records:
            raise VectorNotFoundError(
                f"Không tìm thấy vector: "
                f"{vector_id}"
            )

        del self._records[
            vector_id
        ]

    # =====================================================
    # DELETE BY DOCUMENT
    # =====================================================

    def delete_by_document(
        self,
        document_id: str,
    ) -> int:

        if not document_id:
            raise ValueError(
                "document_id không được rỗng."
            )

        vector_ids = [
            vector_id
            for vector_id, record
            in self._records.items()
            if record.metadata.get(
                "document_id"
            ) == document_id
        ]

        for vector_id in vector_ids:
            del self._records[
                vector_id
            ]

        return len(vector_ids)

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(self) -> None:

        self._records.clear()

    # =====================================================
    # COUNT
    # =====================================================

    def count(self) -> int:

        return len(
            self._records
        )

    # =====================================================
    # VALIDATION
    # =====================================================

    def _validate_vector(
        self,
        vector: list[float],
    ) -> None:

        if not vector:
            raise VectorStoreError(
                "Vector không được rỗng."
            )

        if self.dimension is None:

            self.dimension = len(
                vector
            )

        if len(vector) != self.dimension:
            raise VectorDimensionError(
                "Vector không đúng dimension. "
                f"Expected={self.dimension}, "
                f"Received={len(vector)}."
            )

        for value in vector:

            if not isinstance(
                value,
                (int, float),
            ):
                raise VectorStoreError(
                    "Vector chỉ được chứa số."
                )

            if not math.isfinite(
                float(value)
            ):
                raise VectorStoreError(
                    "Vector chứa giá trị "
                    "không hợp lệ."
                )

    # =====================================================
    # COSINE SIMILARITY
    # =====================================================

    @staticmethod
    def _cosine_similarity(
        vector_a: list[float],
        vector_b: list[float],
    ) -> float:

        if len(vector_a) != len(
            vector_b
        ):
            raise VectorDimensionError(
                "Hai vector phải có cùng dimension."
            )

        dot_product = sum(
            a * b
            for a, b in zip(
                vector_a,
                vector_b,
            )
        )

        norm_a = math.sqrt(
            sum(
                a * a
                for a in vector_a
            )
        )

        norm_b = math.sqrt(
            sum(
                b * b
                for b in vector_b
            )
        )

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return (
            dot_product
            / (norm_a * norm_b)
        )