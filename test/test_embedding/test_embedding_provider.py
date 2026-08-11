from app.knowledge.embedding import (
    BaseEmbeddingProvider,
    EmbeddingError,
)


class FakeEmbeddingProvider(
    BaseEmbeddingProvider
):
    """
    Provider giả dùng cho unit test.

    Không gọi API thật.
    """

    def embed(
        self,
        text: str,
    ) -> list[float]:

        if not text.strip():
            raise EmbeddingError(
                "text không được rỗng."
            )

        return [
            1.0,
            0.0,
            0.0,
        ]


def test_embedding_provider_import():
    assert BaseEmbeddingProvider is not None
    assert EmbeddingError is not None


def test_embedding():
    provider = FakeEmbeddingProvider()

    vector = provider.embed(
        "chuyển đổi số"
    )

    assert isinstance(
        vector,
        list,
    )

    assert vector == [
        1.0,
        0.0,
        0.0,
    ]


def test_embedding_empty_text():
    provider = FakeEmbeddingProvider()

    try:
        provider.embed("")
        assert False
    except EmbeddingError:
        assert True


def test_embedding_whitespace_text():
    provider = FakeEmbeddingProvider()

    try:
        provider.embed("   ")
        assert False
    except EmbeddingError:
        assert True


def test_embed_many():
    provider = FakeEmbeddingProvider()

    vectors = provider.embed_many(
        [
            "chuyển đổi số",
            "cải cách hành chính",
        ]
    )

    assert len(vectors) == 2

    assert vectors[0] == [
        1.0,
        0.0,
        0.0,
    ]

    assert vectors[1] == [
        1.0,
        0.0,
        0.0,
    ]


def test_embed_many_empty():
    provider = FakeEmbeddingProvider()

    vectors = provider.embed_many([])

    assert vectors == []