"""
Tests for ConversationService.

Sprint 13.1.2 - Chat Domain
Conversation Service Layer
"""

import pytest

from app.conversation.conversation import Conversation
from app.conversation.conversation_history import ConversationHistory
from app.conversation.conversation_service import ConversationService


# ============================================================
# CREATE
# ============================================================


def test_create_conversation():
    service = ConversationService()

    conversation = service.create()

    assert isinstance(conversation, Conversation)
    assert conversation.conversation_id
    assert conversation.title == "Cuộc hội thoại mới"
    assert conversation.user_id == "anonymous"

    assert conversation.active is True
    assert conversation.archived is False


def test_create_conversation_with_title():
    service = ConversationService()

    conversation = service.create(
        title="Soạn công văn chuyển đổi số"
    )

    assert conversation.title == (
        "Soạn công văn chuyển đổi số"
    )


def test_create_conversation_with_user_id():
    service = ConversationService()

    conversation = service.create(
        user_id="user-001"
    )

    assert conversation.user_id == "user-001"


def test_create_conversation_with_title_and_user():
    service = ConversationService()

    conversation = service.create(
        title="Hội thoại UBND",
        user_id="canbo-001",
    )

    assert conversation.title == "Hội thoại UBND"
    assert conversation.user_id == "canbo-001"


def test_create_multiple_conversations():
    service = ConversationService()

    first = service.create()
    second = service.create()
    third = service.create()

    assert first.conversation_id != second.conversation_id
    assert second.conversation_id != third.conversation_id
    assert first.conversation_id != third.conversation_id

    assert service.count() == 3


# ============================================================
# GET
# ============================================================


def test_get_existing_conversation():
    service = ConversationService()

    conversation = service.create(
        title="Test Conversation"
    )

    result = service.get(
        conversation.conversation_id
    )

    assert result is conversation


def test_get_missing_conversation_raises_error():
    service = ConversationService()

    with pytest.raises(
        ValueError,
        match="Không tìm thấy Conversation",
    ):
        service.get(
            "conversation-does-not-exist"
        )


def test_get_returns_same_object_after_update():
    service = ConversationService()

    conversation = service.create()

    service.add_user_message(
        conversation.conversation_id,
        "Xin chào",
    )

    result = service.get(
        conversation.conversation_id
    )

    assert result is conversation
    assert result.message_count() == 1


# ============================================================
# USER MESSAGE
# ============================================================


def test_add_user_message():
    service = ConversationService()

    conversation = service.create()

    service.add_user_message(
        conversation.conversation_id,
        "Xin chào",
    )

    history = service.history(
        conversation.conversation_id
    )

    assert isinstance(history, ConversationHistory)
    assert history.count() == 1

    message = history.messages()[0]

    assert message.is_user()
    assert message.content == "Xin chào"


def test_add_multiple_user_messages():
    service = ConversationService()

    conversation = service.create()

    service.add_user_message(
        conversation.conversation_id,
        "Tin nhắn 1",
    )

    service.add_user_message(
        conversation.conversation_id,
        "Tin nhắn 2",
    )

    service.add_user_message(
        conversation.conversation_id,
        "Tin nhắn 3",
    )

    history = service.history(
        conversation.conversation_id
    )

    assert history.count() == 3

    assert history.messages()[0].content == "Tin nhắn 1"
    assert history.messages()[1].content == "Tin nhắn 2"
    assert history.messages()[2].content == "Tin nhắn 3"


def test_add_user_message_preserves_content():
    service = ConversationService()

    conversation = service.create()

    content = (
        "Hãy soạn công văn chỉ đạo "
        "về chuyển đổi số."
    )

    service.add_user_message(
        conversation.conversation_id,
        content,
    )

    message = service.history(
        conversation.conversation_id
    ).messages()[0]

    assert message.content == content


# ============================================================
# ASSISTANT MESSAGE
# ============================================================


def test_add_assistant_message():
    service = ConversationService()

    conversation = service.create()

    service.add_assistant_message(
        conversation.conversation_id,
        "Xin chào, tôi là Hành Chính AI.",
    )

    history = service.history(
        conversation.conversation_id
    )

    assert history.count() == 1

    message = history.messages()[0]

    assert message.is_assistant()
    assert (
        message.content
        == "Xin chào, tôi là Hành Chính AI."
    )


def test_add_assistant_message_with_provider():
    service = ConversationService()

    conversation = service.create()

    service.add_assistant_message(
        conversation.conversation_id,
        "Nội dung trả lời.",
        provider="ollama",
    )

    message = service.history(
        conversation.conversation_id
    ).messages()[0]

    assert message.provider == "ollama"


def test_add_assistant_message_with_model():
    service = ConversationService()

    conversation = service.create()

    service.add_assistant_message(
        conversation.conversation_id,
        "Nội dung trả lời.",
        model="qwen3:8b",
    )

    message = service.history(
        conversation.conversation_id
    ).messages()[0]

    assert message.model == "qwen3:8b"


def test_add_assistant_message_with_tokens():
    service = ConversationService()

    conversation = service.create()

    service.add_assistant_message(
        conversation.conversation_id,
        "Nội dung trả lời.",
        tokens=256,
    )

    message = service.history(
        conversation.conversation_id
    ).messages()[0]

    assert message.tokens == 256


def test_add_assistant_message_with_full_metadata():
    service = ConversationService()

    conversation = service.create()

    service.add_assistant_message(
        conversation.conversation_id,
        "Kết quả trả lời.",
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


# ============================================================
# SYSTEM MESSAGE
# ============================================================


def test_add_system_message():
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

    message = history.messages()[0]

    assert message.is_system()
    assert (
        message.content
        == "Bạn là trợ lý hành chính."
    )


# ============================================================
# MIXED CONVERSATION
# ============================================================


def test_mixed_conversation_message_order():
    service = ConversationService()

    conversation = service.create()

    service.add_system_message(
        conversation.conversation_id,
        "System prompt",
    )

    service.add_user_message(
        conversation.conversation_id,
        "Xin chào",
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Xin chào, tôi có thể giúp gì?",
    )

    history = service.history(
        conversation.conversation_id
    )

    messages = history.messages()

    assert len(messages) == 3

    assert messages[0].is_system()
    assert messages[1].is_user()
    assert messages[2].is_assistant()


def test_last_message_is_assistant():
    service = ConversationService()

    conversation = service.create()

    service.add_user_message(
        conversation.conversation_id,
        "Viết công văn.",
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Tôi sẽ hỗ trợ.",
    )

    history = service.history(
        conversation.conversation_id
    )

    assert (
        history.messages()[-1].is_assistant()
    )


# ============================================================
# HISTORY
# ============================================================


def test_history_returns_conversation_history():
    service = ConversationService()

    conversation = service.create()

    history = service.history(
        conversation.conversation_id
    )

    assert isinstance(
        history,
        ConversationHistory,
    )


def test_history_reflects_new_messages():
    service = ConversationService()

    conversation = service.create()

    history = service.history(
        conversation.conversation_id
    )

    assert history.count() == 0

    service.add_user_message(
        conversation.conversation_id,
        "Xin chào",
    )

    assert history.count() == 1

    service.add_assistant_message(
        conversation.conversation_id,
        "Xin chào bạn.",
    )

    assert history.count() == 2


def test_history_for_missing_conversation():
    service = ConversationService()

    with pytest.raises(
        ValueError,
        match="Không tìm thấy Conversation",
    ):
        service.history(
            "conversation-does-not-exist"
        )


# ============================================================
# PROMPT
# ============================================================


def test_prompt_empty_conversation():
    service = ConversationService()

    conversation = service.create()

    prompt = service.prompt(
        conversation.conversation_id
    )

    assert prompt == ""


def test_prompt_contains_user_message():
    service = ConversationService()

    conversation = service.create()

    service.add_user_message(
        conversation.conversation_id,
        "Viết công văn.",
    )

    prompt = service.prompt(
        conversation.conversation_id
    )

    assert "USER:" in prompt
    assert "Viết công văn." in prompt


def test_prompt_contains_assistant_message():
    service = ConversationService()

    conversation = service.create()

    service.add_assistant_message(
        conversation.conversation_id,
        "Đây là nội dung trả lời.",
    )

    prompt = service.prompt(
        conversation.conversation_id
    )

    assert "ASSISTANT:" in prompt
    assert "Đây là nội dung trả lời." in prompt


def test_prompt_contains_complete_conversation():
    service = ConversationService()

    conversation = service.create()

    service.add_system_message(
        conversation.conversation_id,
        "Bạn là trợ lý hành chính.",
    )

    service.add_user_message(
        conversation.conversation_id,
        "Soạn công văn về chuyển đổi số.",
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Tôi sẽ soạn công văn.",
    )

    prompt = service.prompt(
        conversation.conversation_id
    )

    assert "SYSTEM:" in prompt
    assert "USER:" in prompt
    assert "ASSISTANT:" in prompt

    assert "trợ lý hành chính" in prompt
    assert "chuyển đổi số" in prompt
    assert "Tôi sẽ soạn công văn." in prompt


# ============================================================
# CLEAR
# ============================================================


def test_clear_empty_conversation():
    service = ConversationService()

    conversation = service.create()

    service.clear(
        conversation.conversation_id
    )

    assert (
        service.history(
            conversation.conversation_id
        ).count()
        == 0
    )


def test_clear_conversation_history():
    service = ConversationService()

    conversation = service.create()

    service.add_user_message(
        conversation.conversation_id,
        "Xin chào",
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Xin chào.",
    )

    assert (
        service.history(
            conversation.conversation_id
        ).count()
        == 2
    )

    service.clear(
        conversation.conversation_id
    )

    assert (
        service.history(
            conversation.conversation_id
        ).count()
        == 0
    )


def test_clear_does_not_delete_conversation():
    service = ConversationService()

    conversation = service.create()

    conversation_id = conversation.conversation_id

    service.add_user_message(
        conversation_id,
        "Xin chào",
    )

    service.clear(conversation_id)

    result = service.get(
        conversation_id
    )

    assert result is conversation
    assert result.message_count() == 0
    assert service.count() == 1


# ============================================================
# DELETE
# ============================================================


def test_delete_conversation():
    service = ConversationService()

    conversation = service.create()

    conversation_id = conversation.conversation_id

    assert service.count() == 1

    service.delete(conversation_id)

    assert service.count() == 0

    with pytest.raises(ValueError):
        service.get(conversation_id)


def test_delete_missing_conversation_is_safe():
    service = ConversationService()

    service.delete(
        "conversation-does-not-exist"
    )

    assert service.count() == 0


def test_delete_one_conversation_keeps_others():
    service = ConversationService()

    first = service.create(
        title="Conversation 1"
    )

    second = service.create(
        title="Conversation 2"
    )

    service.delete(
        first.conversation_id
    )

    assert service.count() == 1

    result = service.get(
        second.conversation_id
    )

    assert result is second


# ============================================================
# COUNT / LIST
# ============================================================


def test_count_empty_service():
    service = ConversationService()

    assert service.count() == 0


def test_count_conversations():
    service = ConversationService()

    service.create()
    service.create()
    service.create()

    assert service.count() == 3


def test_list_empty_service():
    service = ConversationService()

    assert service.list() == []


def test_list_conversations():
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


def test_list_after_delete():
    service = ConversationService()

    first = service.create(
        title="Conversation 1"
    )

    second = service.create(
        title="Conversation 2"
    )

    service.delete(
        first.conversation_id
    )

    conversations = service.list()

    assert len(conversations) == 1
    assert conversations[0] is second


# ============================================================
# COMPLETE SERVICE FLOW
# ============================================================


def test_complete_conversation_service_flow():
    service = ConversationService()

    conversation = service.create(
        title="Soạn công văn chuyển đổi số",
        user_id="canbo-001",
    )

    conversation_id = conversation.conversation_id

    # System
    service.add_system_message(
        conversation_id,
        "Bạn là trợ lý hành chính.",
    )

    # User
    service.add_user_message(
        conversation_id,
        "Hãy soạn công văn về chuyển đổi số.",
    )

    # Assistant
    service.add_assistant_message(
        conversation_id,
        "Tôi sẽ hỗ trợ soạn công văn.",
        provider="ollama",
        model="qwen3:8b",
        tokens=128,
    )

    # Verify history
    history = service.history(
        conversation_id
    )

    assert history.count() == 3

    messages = history.messages()

    assert messages[0].is_system()
    assert messages[1].is_user()
    assert messages[2].is_assistant()

    assert messages[2].provider == "ollama"
    assert messages[2].model == "qwen3:8b"
    assert messages[2].tokens == 128

    # Verify prompt
    prompt = service.prompt(
        conversation_id
    )

    assert "SYSTEM:" in prompt
    assert "USER:" in prompt
    assert "ASSISTANT:" in prompt

    assert "chuyển đổi số" in prompt

    # Verify count
    assert service.count() == 1

    # Clear history
    service.clear(conversation_id)

    assert (
        service.history(
            conversation_id
        ).count()
        == 0
    )

    # Conversation itself remains
    assert service.count() == 1

    result = service.get(conversation_id)

    assert result is conversation


# ============================================================
# SERVICE ISOLATION
# ============================================================


def test_each_service_has_independent_cache():
    first_service = ConversationService()
    second_service = ConversationService()

    first_conversation = first_service.create()

    assert first_service.count() == 1
    assert second_service.count() == 0

    with pytest.raises(ValueError):
        second_service.get(
            first_conversation.conversation_id
        )


def test_conversations_are_isolated():
    service = ConversationService()

    first = service.create(
        title="First"
    )

    second = service.create(
        title="Second"
    )

    service.add_user_message(
        first.conversation_id,
        "Message của cuộc hội thoại 1",
    )

    service.add_user_message(
        second.conversation_id,
        "Message của cuộc hội thoại 2",
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
        == "Message của cuộc hội thoại 1"
    )

    assert (
        second_history.messages()[0].content
        == "Message của cuộc hội thoại 2"
    )