"""
Conversation Engine Test
------------------------

Kiểm thử Conversation Engine.
"""

from app.conversation.conversation_service import (
    ConversationService,
)


def test_create_conversation():

    service = ConversationService()

    conversation = service.create(
        title="Test Conversation"
    )

    assert conversation.title == "Test Conversation"

    assert conversation.message_count() == 0


def test_add_user_message():

    service = ConversationService()

    conversation = service.create()

    service.add_user_message(
        conversation.conversation_id,
        "Xin chào"
    )

    history = service.history(
        conversation.conversation_id
    )

    assert history.count() == 1

    assert history.messages()[0].content == "Xin chào"

    assert history.messages()[0].is_user()


def test_add_assistant_message():

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


def test_prompt_generation():

    service = ConversationService()

    conversation = service.create()

    service.add_user_message(
        conversation.conversation_id,
        "Viết công văn."
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Đây là công văn."
    )

    prompt = service.prompt(
        conversation.conversation_id
    )

    assert "USER:" in prompt

    assert "ASSISTANT:" in prompt

    assert "Viết công văn." in prompt

    assert "Đây là công văn." in prompt


def test_clear_history():

    service = ConversationService()

    conversation = service.create()

    service.add_user_message(
        conversation.conversation_id,
        "Hello"
    )

    service.clear(
        conversation.conversation_id
    )

    history = service.history(
        conversation.conversation_id
    )

    assert history.count() == 0


def test_cache_count():

    service = ConversationService()

    service.create()

    service.create()

    service.create()

    assert service.count() == 3