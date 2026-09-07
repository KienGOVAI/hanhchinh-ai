"""
Tests for ConversationHistory.

Sprint 13.1.4 - Chat Domain
Conversation History Layer
"""

from app.conversation.conversation import Conversation
from app.conversation.conversation_history import ConversationHistory
from app.conversation.conversation_message import ConversationMessage


# ============================================================
# INIT
# ============================================================


def test_create_history():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    assert history.conversation is conversation
    assert history.max_messages == 20
    assert history.count() == 0
    assert history.is_empty() is True


def test_create_history_with_custom_limit():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation,
        max_messages=5,
    )

    assert history.max_messages == 5


# ============================================================
# ADD
# ============================================================


def test_add_message():
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


def test_add_multiple_messages():
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

    assert history.count() == 5


def test_add_preserves_message_order():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    first = ConversationMessage(
        role="user",
        content="First",
    )

    second = ConversationMessage(
        role="assistant",
        content="Second",
    )

    third = ConversationMessage(
        role="user",
        content="Third",
    )

    history.add(first)
    history.add(second)
    history.add(third)

    messages = history.messages()

    assert messages[0] is first
    assert messages[1] is second
    assert messages[2] is third


# ============================================================
# MESSAGES
# ============================================================


def test_messages_returns_all_messages():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    first = ConversationMessage(
        role="user",
        content="First",
    )

    second = ConversationMessage(
        role="assistant",
        content="Second",
    )

    history.add(first)
    history.add(second)

    messages = history.messages()

    assert len(messages) == 2
    assert messages[0] is first
    assert messages[1] is second


def test_messages_empty_history():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    assert history.messages() == []


# ============================================================
# LATEST
# ============================================================


def test_latest_returns_recent_messages():
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


def test_latest_returns_all_when_limit_is_larger():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    for index in range(3):
        history.add(
            ConversationMessage(
                role="user",
                content=f"Message {index}",
            )
        )

    latest = history.latest(10)

    assert len(latest) == 3


def test_latest_zero_returns_empty():
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


def test_latest_negative_returns_empty():
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


def test_latest_preserves_order():
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

    latest = history.latest(3)

    assert latest[0].content == "Message 2"
    assert latest[1].content == "Message 3"
    assert latest[2].content == "Message 4"


# ============================================================
# COUNT / EMPTY
# ============================================================


def test_count_empty_history():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    assert history.count() == 0


def test_count_after_add():
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

    assert history.count() == 1


def test_is_empty_initially_true():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    assert history.is_empty() is True


def test_is_empty_after_add_is_false():
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

    assert history.is_empty() is False


# ============================================================
# CLEAR
# ============================================================


def test_clear_history():
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

    history.add(
        ConversationMessage(
            role="assistant",
            content="Xin chào bạn.",
        )
    )

    assert history.count() == 2

    history.clear()

    assert history.count() == 0
    assert history.is_empty() is True
    assert history.messages() == []


def test_clear_empty_history_is_safe():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    history.clear()

    assert history.count() == 0
    assert history.is_empty() is True


# ============================================================
# TRIM
# ============================================================


def test_history_trims_old_messages():
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


def test_history_does_not_trim_before_limit():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation,
        max_messages=3,
    )

    for index in range(3):
        history.add(
            ConversationMessage(
                role="user",
                content=f"Message {index}",
            )
        )

    assert history.count() == 3

    messages = history.messages()

    assert messages[0].content == "Message 0"
    assert messages[1].content == "Message 1"
    assert messages[2].content == "Message 2"


def test_history_trim_keeps_latest_messages():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation,
        max_messages=2,
    )

    history.add(
        ConversationMessage(
            role="user",
            content="Old",
        )
    )

    history.add(
        ConversationMessage(
            role="assistant",
            content="Middle",
        )
    )

    history.add(
        ConversationMessage(
            role="user",
            content="Latest",
        )
    )

    messages = history.messages()

    assert len(messages) == 2
    assert messages[0].content == "Middle"
    assert messages[1].content == "Latest"


def test_history_trim_repeated_additions():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation,
        max_messages=2,
    )

    for index in range(10):
        history.add(
            ConversationMessage(
                role="user",
                content=f"Message {index}",
            )
        )

    assert history.count() == 2

    messages = history.messages()

    assert messages[0].content == "Message 8"
    assert messages[1].content == "Message 9"


# ============================================================
# PROMPT
# ============================================================


def test_to_prompt_empty_history():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    assert history.to_prompt() == ""


def test_to_prompt_user_message():
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

    prompt = history.to_prompt()

    assert "USER:" in prompt
    assert "Viết công văn." in prompt


def test_to_prompt_assistant_message():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    history.add(
        ConversationMessage(
            role="assistant",
            content="Tôi sẽ hỗ trợ.",
        )
    )

    prompt = history.to_prompt()

    assert "ASSISTANT:" in prompt
    assert "Tôi sẽ hỗ trợ." in prompt


def test_to_prompt_system_message():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    history.add(
        ConversationMessage(
            role="system",
            content="Bạn là trợ lý hành chính.",
        )
    )

    prompt = history.to_prompt()

    assert "SYSTEM:" in prompt
    assert "Bạn là trợ lý hành chính." in prompt


def test_to_prompt_complete_conversation():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    history.add(
        ConversationMessage(
            role="system",
            content="Bạn là trợ lý hành chính.",
        )
    )

    history.add(
        ConversationMessage(
            role="user",
            content="Hãy soạn công văn.",
        )
    )

    history.add(
        ConversationMessage(
            role="assistant",
            content="Tôi sẽ soạn công văn.",
        )
    )

    prompt = history.to_prompt()

    assert "SYSTEM:" in prompt
    assert "USER:" in prompt
    assert "ASSISTANT:" in prompt

    assert "Bạn là trợ lý hành chính." in prompt
    assert "Hãy soạn công văn." in prompt
    assert "Tôi sẽ soạn công văn." in prompt


def test_to_prompt_preserves_message_order():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation
    )

    history.add(
        ConversationMessage(
            role="user",
            content="Câu hỏi",
        )
    )

    history.add(
        ConversationMessage(
            role="assistant",
            content="Câu trả lời",
        )
    )

    prompt = history.to_prompt()

    user_position = prompt.index("USER:")
    assistant_position = prompt.index(
        "ASSISTANT:"
    )

    assert user_position < assistant_position


# ============================================================
# CONVERSATION LINK
# ============================================================


def test_history_operates_on_original_conversation():
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

    assert conversation.message_count() == 1
    assert conversation.last_message() is (
        history.messages()[-1]
    )


def test_history_clear_updates_original_conversation():
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

    assert conversation.message_count() == 1

    history.clear()

    assert conversation.message_count() == 0
    assert conversation.is_empty() is True


# ============================================================
# COMPLETE HISTORY FLOW
# ============================================================


def test_complete_history_flow():
    conversation = Conversation(
        conversation_id="conversation-001"
    )

    history = ConversationHistory(
        conversation=conversation,
        max_messages=4,
    )

    history.add(
        ConversationMessage(
            role="system",
            content="Bạn là trợ lý hành chính.",
        )
    )

    history.add(
        ConversationMessage(
            role="user",
            content="Soạn công văn.",
        )
    )

    history.add(
        ConversationMessage(
            role="assistant",
            content="Tôi sẽ hỗ trợ.",
        )
    )

    history.add(
        ConversationMessage(
            role="user",
            content="Về chuyển đổi số.",
        )
    )

    assert history.count() == 4
    assert history.is_empty() is False

    latest = history.latest(2)

    assert len(latest) == 2
    assert latest[0].content == "Tôi sẽ hỗ trợ."
    assert latest[1].content == "Về chuyển đổi số."

    prompt = history.to_prompt()

    assert "SYSTEM:" in prompt
    assert "USER:" in prompt
    assert "ASSISTANT:" in prompt
    assert "chuyển đổi số" in prompt

    history.clear()

    assert history.count() == 0
    assert history.is_empty() is True
    assert history.to_prompt() == ""