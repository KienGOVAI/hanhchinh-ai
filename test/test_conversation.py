"""
Tests for Conversation Engine
Sprint 13.1 - Chat Domain
"""

import pytest

from app.conversation.conversation import Conversation
from app.conversation.conversation_cache import ConversationCache
from app.conversation.conversation_history import ConversationHistory
from app.conversation.conversation_message import ConversationMessage
from app.conversation.conversation_service import ConversationService


# ============================================================
# Conversation
# ============================================================


def test_create_conversation():
    service = ConversationService()

    conversation = service.create(
        title="Test Conversation"
    )

    assert isinstance(conversation, Conversation)
    assert conversation.conversation_id
    assert conversation.user_id == "anonymous"
    assert conversation.title == "Test Conversation"

    assert conversation.active is True
    assert conversation.archived is False

    assert conversation.message_count() == 0
    assert conversation.is_empty() is True
    assert conversation.last_message() is None


def test_create_conversation_with_user():
    service = ConversationService()

    conversation = service.create(
        title="Hội thoại cán bộ",
        user_id="user-001",
    )

    assert conversation.user_id == "user-001"
    assert conversation.title == "Hội thoại cán bộ"


def test_conversation_identity_is_unique():
    service = ConversationService()

    first = service.create()
    second = service.create()

    assert first.conversation_id
    assert second.conversation_id
    assert first.conversation_id != second.conversation_id


def test_conversation_timestamps_exist():
    service = ConversationService()

    conversation = service.create()

    assert conversation.created_at is not None
    assert conversation.updated_at is not None


# ============================================================
# ConversationMessage
# ============================================================


def test_user_message():
    message = ConversationMessage(
        role="user",
        content="Xin chào",
    )

    assert message.is_user() is True
    assert message.is_assistant() is False
    assert message.is_system() is False
    assert message.has_content() is True


def test_assistant_message():
    message = ConversationMessage(
        role="assistant",
        content="Xin chào, tôi là Hành Chính AI.",
        provider="ollama",
        model="qwen3:8b",
        tokens=120,
    )

    assert message.is_assistant() is True
    assert message.is_user() is False
    assert message.is_system() is False

    assert message.provider == "ollama"
    assert message.model == "qwen3:8b"
    assert message.tokens == 120


def test_system_message():
    message = ConversationMessage(
        role="system",
        content="Bạn là trợ lý hành chính.",
    )

    assert message.is_system() is True
    assert message.is_user() is False
    assert message.is_assistant() is False


def test_message_has_content():
    message = ConversationMessage(
        role="user",
        content="  Xin chào  ",
    )

    assert message.has_content() is True


def test_empty_message_is_rejected():
    with pytest.raises(
        ValueError,
        match="content không được rỗng",
    ):
        ConversationMessage(
            role="user",
            content="   ",
        )


def test_message_preview_short_content():
    message = ConversationMessage(
        role="user",
        content="Xin chào",
    )

    assert message.preview() == "Xin chào"


def test_message_preview_long_content():
    content = "A" * 100

    message = ConversationMessage(
        role="user",
        content=content,
    )

    preview = message.preview(80)

    assert len(preview) == 83
    assert preview.endswith("...")


# ============================================================
# Conversation message management
# ============================================================


def test_add_message():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    message = ConversationMessage(
        role="user",
        content="Xin chào",
    )

    conversation.add_message(message)

    assert conversation.message_count() == 1
    assert conversation.is_empty() is False
    assert conversation.last_message() is message


def test_last_message_returns_latest_message():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    first = ConversationMessage(
        role="user",
        content="Tin nhắn đầu",
    )

    second = ConversationMessage(
        role="assistant",
        content="Tin nhắn sau",
    )

    conversation.add_message(first)
    conversation.add_message(second)

    assert conversation.message_count() == 2
    assert conversation.last_message() is second


def test_clear_conversation():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    conversation.add_message(
        ConversationMessage(
            role="user",
            content="Xin chào",
        )
    )

    assert conversation.is_empty() is False

    conversation.clear()

    assert conversation.is_empty() is True
    assert conversation.message_count() == 0
    assert conversation.last_message() is None


# ============================================================
# ConversationHistory
# ============================================================


def test_history_add_message():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    message = ConversationMessage(
        role="user",
        content="Xin chào",
    )

    history.add(message)

    assert history.count() == 1
    assert history.messages()[0] is message


def test_history_latest():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    for index in range(5):
        history.add(
            ConversationMessage(
                role="user",
                content=f"Message {index}",
            )
        )

    latest = history.latest(2)

    assert len(latest) == 2
    assert latest[0].content == "Message 3"
    assert latest[1].content == "Message 4"


def test_history_latest_with_zero_limit():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    history.add(
        ConversationMessage(
            role="user",
            content="Xin chào",
        )
    )

    assert history.latest(0) == []


def test_history_latest_with_negative_limit():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    history.add(
        ConversationMessage(
            role="user",
            content="Xin chào",
        )
    )

    assert history.latest(-1) == []


def test_history_count():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    assert history.count() == 0

    history.add(
        ConversationMessage(
            role="user",
            content="Xin chào",
        )
    )

    assert history.count() == 1


def test_history_empty():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    assert history.is_empty() is True

    history.add(
        ConversationMessage(
            role="user",
            content="Xin chào",
        )
    )

    assert history.is_empty() is False


def test_history_clear():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    history.add(
        ConversationMessage(
            role="user",
            content="Xin chào",
        )
    )

    history.clear()

    assert history.count() == 0
    assert history.is_empty() is True


def test_history_to_prompt():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    history.add(
        ConversationMessage(
            role="user",
            content="Viết công văn.",
        )
    )

    history.add(
        ConversationMessage(
            role="assistant",
            content="Đây là công văn.",
        )
    )

    prompt = history.to_prompt()

    assert "USER:" in prompt
    assert "ASSISTANT:" in prompt

    assert "Viết công văn." in prompt
    assert "Đây là công văn." in prompt


def test_empty_history_to_prompt():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    assert history.to_prompt() == ""


def test_history_trim():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation,
        max_messages=3,
    )

    for index in range(5):
        history.add(
            ConversationMessage(
                role="user",
                content=f"Message {index}",
            )
        )

    assert history.count() == 3

    messages = history.messages()

    assert messages[0].content == "Message 2"
    assert messages[1].content == "Message 3"
    assert messages[2].content == "Message 4"


# ============================================================
# ConversationCache
# ============================================================


def test_cache_set_and_get():
    cache = ConversationCache()

    conversation = Conversation(
        conversation_id="conversation-001"
    )

    cache.set(conversation)

    result = cache.get(
        "conversation-001"
    )

    assert result is conversation


def test_cache_exists():
    cache = ConversationCache()

    conversation = Conversation(
        conversation_id="conversation-001"
    )

    assert cache.exists(
        "conversation-001"
    ) is False

    cache.set(conversation)

    assert cache.exists(
        "conversation-001"
    ) is True


def test_cache_remove():
    cache = ConversationCache()

    conversation = Conversation(
        conversation_id="conversation-001"
    )

    cache.set(conversation)

    assert cache.exists(
        "conversation-001"
    ) is True

    cache.remove(
        "conversation-001"
    )

    assert cache.exists(
        "conversation-001"
    ) is False


def test_cache_clear():
    cache = ConversationCache()

    cache.set(
        Conversation(
            conversation_id="conversation-001"
        )
    )

    cache.set(
        Conversation(
            conversation_id="conversation-002"
        )
    )

    assert cache.count() == 2

    cache.clear()

    assert cache.count() == 0
    assert cache.list() == []


def test_cache_list():
    cache = ConversationCache()

    first = Conversation(
        conversation_id="conversation-001"
    )

    second = Conversation(
        conversation_id="conversation-002"
    )

    cache.set(first)
    cache.set(second)

    conversations = cache.list()

    assert len(conversations) == 2
    assert first in conversations
    assert second in conversations


def test_cache_count():
    cache = ConversationCache()

    assert cache.count() == 0

    cache.set(
        Conversation(
            conversation_id="conversation-001"
        )
    )

    cache.set(
        Conversation(
            conversation_id="conversation-002"
        )
    )

    cache.set(
        Conversation(
            conversation_id="conversation-003"
        )
    )

    assert cache.count() == 3


# ============================================================
# ConversationService
# ============================================================


def test_service_get_conversation():
    service = ConversationService()

    conversation = service.create(
        title="Test Conversation"
    )

    result = service.get(
        conversation.conversation_id
    )

    assert result is conversation


def test_service_get_missing_conversation():
    service = ConversationService()

    with pytest.raises(ValueError):
        service.get(
            "conversation-does-not-exist"
        )


def test_service_add_user_message():
    service = ConversationService()

    conversation = service.create()

    service.add_user_message(
        conversation.conversation_id,
        "Xin chào",
    )

    history = service.history(
        conversation.conversation_id
    )

    assert history.count() == 1
    assert history.messages()[0].content == "Xin chào"
    assert history.messages()[0].is_user()


def test_service_add_assistant_message():
    service = ConversationService()

    conversation = service.create()

    service.add_assistant_message(
        conversation.conversation_id,
        "Xin chào, tôi là Hành Chính AI.",
        provider="ollama",
        model="qwen3:8b",
        tokens=120,
    )

    history = service.history(
        conversation.conversation_id
    )

    message = history.messages()[0]

    assert message.is_assistant()
    assert message.provider == "ollama"
    assert message.model == "qwen3:8b"
    assert message.tokens == 120


def test_service_add_system_message():
    service = ConversationService()

    conversation = service.create()

    service.add_system_message(
        conversation.conversation_id,
        "Bạn là trợ lý hành chính.",
    )

    history = service.history(
        conversation.conversation_id
    )

    assert history.count() == 1
    assert history.messages()[0].is_system()


def test_service_prompt_generation():
    service = ConversationService()

    conversation = service.create()

    service.add_user_message(
        conversation.conversation_id,
        "Viết công văn.",
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Đây là công văn.",
    )

    prompt = service.prompt(
        conversation.conversation_id
    )

    assert "USER:" in prompt
    assert "ASSISTANT:" in prompt

    assert "Viết công văn." in prompt
    assert "Đây là công văn." in prompt


def test_service_clear_history():
    service = ConversationService()

    conversation = service.create()

    service.add_user_message(
        conversation.conversation_id,
        "Hello",
    )

    service.clear(
        conversation.conversation_id
    )

    history = service.history(
        conversation.conversation_id
    )

    assert history.count() == 0


def test_service_delete_conversation():
    service = ConversationService()

    conversation = service.create()

    conversation_id = conversation.conversation_id

    assert service.count() == 1

    service.delete(conversation_id)

    assert service.count() == 0

    with pytest.raises(ValueError):
        service.get(conversation_id)


def test_service_list_conversations():
    service = ConversationService()

    first = service.create(
        title="Conversation 1"
    )

    second = service.create(
        title="Conversation 2"
    )

    conversations = service.list()

    assert len(conversations) == 2
    assert first in conversations
    assert second in conversations


def test_service_count():
    service = ConversationService()

    service.create()
    service.create()
    service.create()

    assert service.count() == 3


# ============================================================
# Complete Conversation Domain flow
# ============================================================


def test_complete_conversation_flow():
    service = ConversationService()

    conversation = service.create(
        title="Soạn công văn chuyển đổi số",
        user_id="canbo-001",
    )

    service.add_system_message(
        conversation.conversation_id,
        "Bạn là trợ lý hành chính.",
    )

    service.add_user_message(
        conversation.conversation_id,
        "Hãy soạn công văn về chuyển đổi số.",
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Tôi sẽ hỗ trợ soạn công văn.",
        provider="ollama",
        model="qwen3:8b",
        tokens=100,
    )

    history = service.history(
        conversation.conversation_id
    )

    assert history.count() == 3
    assert history.is_empty() is False

    messages = history.messages()

    assert messages[0].is_system()
    assert messages[1].is_user()
    assert messages[2].is_assistant()

    assert conversation.last_message() is messages[2]

    prompt = service.prompt(
        conversation.conversation_id
    )

    assert "SYSTEM:" in prompt
    assert "USER:" in prompt
    assert "ASSISTANT:" in prompt

    assert "chuyển đổi số" in prompt

    service.clear(
        conversation.conversation_id
    )

    assert service.history(
        conversation.conversation_id
    ).is_empty()