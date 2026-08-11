"""
Application entry point.

Hành Chính AI
Sprint 12

Assistant Runtime - Task 12.14.9 Layer 1.

Pipeline:

    HTTP
      ↓
    AssistantService
      ↓
    DemoEmbeddingProvider
      ↓
    Retriever
      ↓
    ContextBuilder
      ↓
    RAGService
      ↓
    AI Provider
      ↓
    CitationService
      ↓
    Answer + Citations
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.document import router as document_router

from app.api.routes.knowledge import (
    configure_knowledge_service,
    router as knowledge_router,
)

from app.api.routes.assistant import (
    configure_assistant_service,
    router as assistant_router,
)

from app.core.config import (
    APP_NAME,
    APP_VERSION,
)

from app.knowledge.assistant import (
    AssistantService,
)

from app.knowledge.citation import (
    CitationService,
)

from app.knowledge.context import (
    ContextBuilder,
)

from app.knowledge.embedding import (
    DemoEmbeddingProvider,
)

from app.knowledge.rag import (
    RAGService,
)

from app.knowledge.retrieval import (
    Retriever,
)

from app.knowledge.services.knowledge_service import (
    KnowledgeService,
)

from app.knowledge.vectorstore import (
    LocalVectorStore,
    VectorRecord,
)

from app.providers.provider_factory import (
    ProviderFactory,
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title=APP_NAME,
    description=(
        "Trợ lý AI dành cho cơ quan hành chính Việt Nam"
    ),
    version=APP_VERSION,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# KNOWLEDGE RUNTIME
# ============================================================

def create_knowledge_runtime() -> tuple[
    LocalVectorStore,
    KnowledgeService,
]:
    """
    Khởi tạo Knowledge runtime.

    Architecture:

        LocalVectorStore
              ↓
           Retriever
              ↓
        KnowledgeService
    """

    vector_store = LocalVectorStore()

    retriever = Retriever(
        vector_store=vector_store,
        default_top_k=5,
        score_threshold=0.0,
    )

    knowledge_service = KnowledgeService(
        retriever=retriever,
    )

    return (
        vector_store,
        knowledge_service,
    )


knowledge_vector_store, knowledge_service = (
    create_knowledge_runtime()
)


# ============================================================
# KNOWLEDGE DEMO DATA
# ============================================================

def seed_knowledge_demo_data(
    vector_store: LocalVectorStore,
) -> None:
    """
    Nạp dữ liệu Knowledge Demo.

    Các vector demo đều có dimension = 3.

    Chỉ sử dụng khi:

        KNOWLEDGE_DEMO_MODE=true
    """

    vector_store.add_many(
        [
            VectorRecord(
                vector_id="demo-chunk-001",
                vector=[
                    1.0,
                    0.0,
                    0.0,
                ],
                metadata={
                    "document_id": (
                        "demo-nghi-quyet-57"
                    ),
                    "chunk_index": 0,
                    "page_number": 1,
                    "content": (
                        "Chuyển đổi số là quá trình "
                        "ứng dụng công nghệ số vào hoạt động "
                        "quản lý, điều hành và cung cấp dịch vụ, "
                        "nhằm nâng cao hiệu quả hoạt động "
                        "của cơ quan hành chính."
                    ),
                    "document_name": (
                        "Nghị quyết - Demo Knowledge Base"
                    ),
                    "source": (
                        "Nghị quyết - Demo Knowledge Base"
                    ),
                },
            ),
            VectorRecord(
                vector_id="demo-chunk-002",
                vector=[
                    0.95,
                    0.05,
                    0.0,
                ],
                metadata={
                    "document_id": (
                        "demo-ke-hoach-cds"
                    ),
                    "chunk_index": 1,
                    "page_number": 3,
                    "content": (
                        "Triển khai chuyển đổi số cần gắn "
                        "với cải cách hành chính, nâng cao "
                        "chất lượng phục vụ người dân và "
                        "doanh nghiệp."
                    ),
                    "document_name": (
                        "Kế hoạch chuyển đổi số - Demo"
                    ),
                    "source": (
                        "Kế hoạch chuyển đổi số - Demo"
                    ),
                },
            ),
        ]
    )


# ============================================================
# ENABLE KNOWLEDGE DEMO MODE
# ============================================================

knowledge_demo_mode = (
    os.getenv(
        "KNOWLEDGE_DEMO_MODE",
        "false",
    ).lower()
    == "true"
)

if knowledge_demo_mode:
    seed_knowledge_demo_data(
        knowledge_vector_store
    )


# ============================================================
# CONFIGURE KNOWLEDGE SERVICE
# ============================================================

configure_knowledge_service(
    knowledge_service
)


# ============================================================
# ASSISTANT RUNTIME
# ============================================================

def create_assistant_runtime(
    retriever: Retriever,
) -> AssistantService:
    """
    Khởi tạo toàn bộ Assistant Runtime.

    Layer 1 - Integration Demo:

        Question
            ↓
        DemoEmbeddingProvider
            ↓
        Retriever
            ↓
        ContextBuilder
            ↓
        RAGService
            ↓
        AI Provider
            ↓
        CitationService
            ↓
        AssistantService
    """

    # --------------------------------------------------------
    # EMBEDDING
    # --------------------------------------------------------

    embedding_provider = (
        DemoEmbeddingProvider()
    )

    # --------------------------------------------------------
    # CONTEXT
    # --------------------------------------------------------

    context_builder = ContextBuilder(
        max_chunks=5,
    )

    # --------------------------------------------------------
    # GENERATION PROVIDER
    # --------------------------------------------------------

    generation_provider = (
        ProviderFactory.create()
    )

    # --------------------------------------------------------
    # RAG
    # --------------------------------------------------------

    rag_service = RAGService(
        retriever=retriever,
        embedding_service=embedding_provider,
        generation_provider=(
            generation_provider
        ),
        context_builder=context_builder,
        top_k=5,
        score_threshold=0.0,
    )

    # --------------------------------------------------------
    # CITATION
    # --------------------------------------------------------

    citation_service = CitationService()

    # --------------------------------------------------------
    # ASSISTANT
    # --------------------------------------------------------

    assistant_service = AssistantService(
        embedding_provider=embedding_provider,
        retriever=retriever,
        context_builder=context_builder,
        rag_service=rag_service,
        citation_service=citation_service,
    )

    return assistant_service


assistant_service = create_assistant_runtime(
    retriever=knowledge_service.retriever,
)


# ============================================================
# CONFIGURE ASSISTANT API
# ============================================================

configure_assistant_service(
    assistant_service
)


# ============================================================
# API ROUTERS
# ============================================================

app.include_router(
    health_router
)

app.include_router(
    document_router
)

app.include_router(
    knowledge_router
)

app.include_router(
    assistant_router
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "project": APP_NAME,
        "status": "Running",
        "version": APP_VERSION,
        "message": (
            "Chào mừng bạn đến với Hành Chính AI!"
        ),
    }