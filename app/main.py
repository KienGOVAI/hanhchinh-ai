"""
Hành Chính AI
Sprint 17

Authentication Runtime - Login / JWT / RBAC / Protected API.
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
    configure_conversation_service,
    router as assistant_router,
)

from app.api.routes.ocr import (
    router as ocr_router,
)

from app.api.routes.voice import (
    configure_voice_ai_service,
    router as voice_router,
)

from app.api.routes.voice_document import (
    router as voice_document_router,
)

from app.api.routes.voice_conversation import (
    router as voice_conversation_router,
)

from app.api.routes.workflow import (
    router as workflow_router,
)

from app.api.routes.auth import (
    configure_auth_services,
    router as auth_router,
)

from app.api.routes.protected import (
    router as protected_router,
)

from app.ocr.runtime import (
    configure_ocr_ai_service,
)

from app.ocr.rag_runtime import (
    configure_ocr_rag_service,
)

from app.auth.jwt import JWTService
from app.auth.service import UserService

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

from app.conversation.conversation_service import (
    ConversationService,
)

from app.voice.ai import (
    VoiceAIService,
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
# CONVERSATION RUNTIME
# ============================================================

conversation_service = ConversationService()

configure_conversation_service(
    conversation_service
)


# ============================================================
# OCR RUNTIME
# ============================================================

configure_ocr_ai_service(
    assistant_service
)

configure_ocr_rag_service(
    assistant_service
)


# ============================================================
# VOICE RUNTIME
# ============================================================

voice_ai_service = VoiceAIService(
    assistant_service,
)

configure_voice_ai_service(
    voice_ai_service
)


# ============================================================
# AUTH RUNTIME
# ============================================================

auth_user_service = UserService()

auth_jwt_service = JWTService()

configure_auth_services(
    auth_user_service,
    auth_jwt_service,
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

app.include_router(
    ocr_router
)

app.include_router(
    voice_router
)

app.include_router(
    voice_document_router
)

app.include_router(
    voice_conversation_router
)

app.include_router(
    workflow_router
)

app.include_router(
    auth_router
)

app.include_router(
    protected_router
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