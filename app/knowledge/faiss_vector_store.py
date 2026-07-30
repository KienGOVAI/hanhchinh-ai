"""
FAISS Vector Store
------------------

Vector Store sử dụng Facebook AI Similarity Search (FAISS).
"""

import pickle
from pathlib import Path
from typing import List

import faiss
import numpy as np

from app.knowledge.vector_store import VectorStore
from app.knowledge.text_chunk import TextChunk


class FAISSVectorStore(VectorStore):

    def __init__(self):

        self.index = None

        self.dimension = None

        self.chunks: List[TextChunk] = []

    # =====================================================

    def add(
        self,
        chunks: List[TextChunk],
    ) -> None:

        if not chunks:
            return

        vectors = np.array(
            [chunk.embedding for chunk in chunks],
            dtype="float32",
        )

        if self.index is None:

            self.dimension = vectors.shape[1]

            self.index = faiss.IndexFlatIP(
                self.dimension
            )

        self.index.add(vectors)

        self.chunks.extend(chunks)

    # =====================================================

    def search(
        self,
        embedding: List[float],
        top_k: int = 5,
    ) -> List[TextChunk]:

        if self.index is None:
            return []

        query = np.array(
            [embedding],
            dtype="float32",
        )

        scores, indices = self.index.search(
            query,
            top_k,
        )

        results = []

        for score, idx in zip(
            scores[0],
            indices[0],
        ):

            if idx < 0:
                continue

            chunk = self.chunks[idx]

            chunk.score = float(score)

            results.append(chunk)

        return results

    # =====================================================

    def save(
        self,
        directory: str,
    ) -> None:

        path = Path(directory)

        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        faiss.write_index(
            self.index,
            str(path / "index.faiss"),
        )

        with open(
            path / "chunks.pkl",
            "wb",
        ) as f:

            pickle.dump(
                self.chunks,
                f,
            )

    # =====================================================

    def load(
        self,
        directory: str,
    ) -> None:

        path = Path(directory)

        self.index = faiss.read_index(
            str(path / "index.faiss")
        )

        self.dimension = self.index.d

        with open(
            path / "chunks.pkl",
            "rb",
        ) as f:

            self.chunks = pickle.load(f)

    # =====================================================

    def count(self) -> int:

        if self.index is None:
            return 0

        return self.index.ntotal

    # =====================================================

    def clear(self) -> None:

        self.index = None

        self.dimension = None

        self.chunks.clear()