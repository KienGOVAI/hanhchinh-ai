"""
Conversation Integration Tests.

Sprint 13.1.6 - Chat Domain
Conversation Engine Integration
"""

from app.conversation.conversation import Conversation
from app.conversation.conversation_cache import ConversationCache
from app.conversation.conversation_history import (
    ConversationHistory,
)
from app.conversation.conversation_message import (
    ConversationMessage,
)
from app.conversation.conversation_service import (
    ConversationService,
)


# ============================================================
# COMPLETE CONVERSATION FLOW
# ============================================================


def test_complete_conversation_flow():
    service = ConversationService()

    conversation = service.create(
        title="Tra cứu chuyển đổi số",
        user_id="user-001",
    )

    assert conversation.conversation_id
    assert conversation.title == "Tra cứu chuyển đổi số"
    assert conversation.user_id == "user-001"
    assert conversation.is_empty() is True

    service.add_user_message(
        conversation.conversation_id,
        "Chuyển đổi số ở cấp xã là gì?",
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Chuyển đổi số là quá trình ứng dụng công nghệ "
        "số để nâng cao hiệu quả quản lý và chất lượng "
        "phục vụ người dân.",
        provider="ollama",
        model="qwen3:8b",
        tokens=120,
    )

    history = service.history(
        conversation.conversation_id
    )

    assert history.count() == 2
    assert history.is_empty() is False

    messages = history.messages()

    assert messages[0].is_user()
    assert messages[1].is_assistant()

    assert (
        "Chuyển đổi số"
        in messages[0].content
    )

    assert (
        "công nghệ"
        in messages[1].content
    )

    prompt = service.prompt(
        conversation.conversation_id
    )

    assert "USER:" in prompt
    assert "ASSISTANT:" in prompt
    assert "Chuyển đổi số" in prompt
    assert "công nghệ" in prompt


# ============================================================
# USER → ASSISTANT → USER → ASSISTANT
# ============================================================


def test_multi_turn_conversation():
    service = ConversationService()

    conversation = service.create()

    service.add_user_message(
        conversation.conversation_id,
        "Hãy giải thích RAG.",
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "RAG là cơ chế truy xuất thông tin "
        "trước khi tạo câu trả lời.",
        provider="ollama",
        model="qwen3:8b",
    )

    service.add_user_message(
        conversation.conversation_id,
        "RAG có thể dùng cho văn bản pháp luật không?",
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Có. RAG có thể truy xuất Luật, "
        "Nghị định, Thông tư và các văn bản liên quan.",
        provider="ollama",
        model="qwen3:8b",
    )

    history = service.history(
        conversation.conversation_id
    )

    assert history.count() == 4

    messages = history.messages()

    assert messages[0].role == "user"
    assert messages[1].role == "assistant"
    assert messages[2].role == "user"
    assert messages[3].role == "assistant"

    prompt = service.prompt(
        conversation.conversation_id
    )

    assert prompt.index("USER:") < prompt.index(
        "ASSISTANT:"
    )


# ============================================================
# SYSTEM + USER + ASSISTANT
# ============================================================


def test_system_user_assistant_flow():
    service = ConversationService()

    conversation = service.create()

    service.add_system_message(
        conversation.conversation_id,
        "Bạn là trợ lý AI của UBND xã.",
    )

    service.add_user_message(
        conversation.conversation_id,
        "Soạn công văn về chuyển đổi số.",
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Tôi sẽ hỗ trợ soạn công văn.",
        provider="ollama",
        model="qwen3:8b",
    )

    history = service.history(
        conversation.conversation_id
    )

    assert history.count() == 3

    messages = history.messages()

    assert messages[0].is_system()
    assert messages[1].is_user()
    assert messages[2].is_assistant()

    prompt = history.to_prompt()

    assert "SYSTEM:" in prompt
    assert "USER:" in prompt
    assert "ASSISTANT:" in prompt


# ============================================================
# CACHE + SERVICE
# ============================================================


def test_service_and_cache_are_connected():
    service = ConversationService()

    conversation = service.create()

    assert service.count() == 1

    cached = service.cache.get(
        conversation.conversation_id
    )

    assert cached is conversation


def test_multiple_conversations_are_independent():
    service = ConversationService()

    first = service.create(
        title="Conversation 1"
    )

    second = service.create(
        title="Conversation 2"
    )

    service.add_user_message(
        first.conversation_id,
        "Nội dung 1",
    )

    service.add_user_message(
        second.conversation_id,
        "Nội dung 2",
    )

    first_history = service.history(
        first.conversation_id
    )

    second_history = service.history(
        second.conversation_id
    )

    assert first_history.count() == 1
    assert second_history.count() == 1

    assert (
        first_history.messages()[0].content
        == "Nội dung 1"
    )

    assert (
        second_history.messages()[0].content
        == "Nội dung 2"
    )


def test_delete_conversation_removes_it_from_cache():
    service = ConversationService()

    conversation = service.create()

    conversation_id = conversation.conversation_id

    assert service.cache.exists(
        conversation_id
    )

    service.delete(conversation_id)

    assert not service.cache.exists(
        conversation_id
    )


# ============================================================
# HISTORY LIMIT
# ============================================================


def test_history_limit_keeps_latest_messages():
    conversation = Conversation(
        conversation_id="integration-001"
    )

    history = ConversationHistory(
        conversation=conversation,
        max_messages=4,
    )

    for index in range(8):
        history.add(
            ConversationMessage(
                role="user",
                content=f"Message {index}",
            )
        )

    assert history.count() == 4

    messages = history.messages()

    assert messages[0].content == "Message 4"
    assert messages[1].content == "Message 5"
    assert messages[2].content == "Message 6"
    assert messages[3].content == "Message 7"


# ============================================================
# PROMPT AFTER TRIM
# ============================================================


def test_prompt_contains_only_retained_history():
    conversation = Conversation(
        conversation_id="integration-002"
    )

    history = ConversationHistory(
        conversation=conversation,
        max_messages=2,
    )

    history.add(
        ConversationMessage(
            role="user",
            content="Tin nhắn cũ",
        )
    )

    history.add(
        ConversationMessage(
            role="user",
            content="Tin nhắn giữa",
        )
    )

    history.add(
        ConversationMessage(
            role="assistant",
            content="Tin nhắn mới",
        )
    )

    prompt = history.to_prompt()

    assert "Tin nhắn cũ" not in prompt
    assert "Tin nhắn giữa" in prompt
    assert "Tin nhắn mới" in prompt


# ============================================================
# MESSAGE METADATA THROUGH SERVICE
# ============================================================


def test_assistant_metadata_survives_service_flow():
    service = ConversationService()

    conversation = service.create()

    service.add_assistant_message(
        conversation.conversation_id,
        "Đã hoàn thành.",
        provider="ollama",
        model="qwen3:8b",
        tokens=512,
    )

    message = service.history(
        conversation.conversation_id
    ).messages()[0]

    assert message.is_assistant()
    assert message.provider == "ollama"
    assert message.model == "qwen3:8b"
    assert message.tokens == 512
    assert message.error is False


# ============================================================
# CLEAR FLOW
# ============================================================


def test_clear_history_preserves_conversation():
    service = ConversationService()

    conversation = service.create(
        title="Test Clear"
    )

    service.add_user_message(
        conversation.conversation_id,
        "Xin chào",
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Xin chào bạn.",
    )

    assert service.count() == 1

    service.clear(
        conversation.conversation_id
    )

    assert service.count() == 1

    restored = service.get(
        conversation.conversation_id
    )

    assert restored is conversation
    assert restored.title == "Test Clear"
    assert restored.is_empty() is True


# ============================================================
# CACHE DIRECT CONTRACT
# ============================================================


def test_cache_direct_flow():
    cache = ConversationCache()

    conversation = Conversation(
        conversation_id="cache-integration-001",
        title="Cache Test",
    )

    assert cache.count() == 0
    assert cache.exists(
        conversation.conversation_id
    ) is False

    cache.set(conversation)

    assert cache.count() == 1
    assert cache.exists(
        conversation.conversation_id
    ) is True

    retrieved = cache.get(
        conversation.conversation_id
    )

    assert retrieved is conversation

    cache.remove(
        conversation.conversation_id
    )

    assert cache.count() == 0
    assert cache.exists(
        conversation.conversation_id
    ) is False


# ============================================================
# FINAL END-TO-END CONTRACT
# ============================================================


def test_conversation_engine_end_to_end():
    service = ConversationService()

    conversation = service.create(
        title="Hành Chính AI",
        user_id="officer-001",
    )

    service.add_system_message(
        conversation.conversation_id,
        "Bạn là Hành Chính AI, trợ lý hành chính.",
    )

    service.add_user_message(
        conversation.conversation_id,
        "Hãy hỗ trợ tôi soạn công văn.",
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Tôi có thể hỗ trợ soạn công văn "
        "theo thể thức hành chính.",
        provider="ollama",
        model="qwen3:8b",
        tokens=256,
    )

    history = service.history(
        conversation.conversation_id
    )

    assert history.count() == 3

    assert history.messages()[0].is_system()
    assert history.messages()[1].is_user()
    assert history.messages()[2].is_assistant()

    last = history.messages()[-1]

    assert last.provider == "ollama"
    assert last.model == "qwen3:8b"
    assert last.tokens == 256

    prompt = service.prompt(
        conversation.conversation_id
    )

    assert "SYSTEM:" in prompt
    assert "USER:" in prompt
    assert "ASSISTANT:" in prompt

    assert "Hành Chính AI" in prompt
    assert "soạn công văn" in prompt

    assert service.count() == 1

    assert service.get(
        conversation.conversation_id
    ) is conversation