"""
Sprint 13.5
Context / Memory

Kiểm thử Context + Conversation Memory.

Mục tiêu:

    User Message
          ↓
    Conversation
          ↓
    ConversationHistory
          ↓
    Context / Prompt
          ↓
    AI sử dụng được lịch sử hội thoại

Không gọi AI thật.
Không gọi Ollama.
Không gọi RAG thật.

Chỉ kiểm tra contract của Conversation Memory.
"""

from app.conversation.conversation_service import (
    ConversationService,
)
from app.conversation.conversation_history import (
    ConversationHistory,
)
from app.conversation.conversation_message import (
    ConversationMessage,
)


# =========================================================
# HELPERS
# =========================================================


def create_conversation(
    *,
    title: str = "Test Conversation",
    user_id: str = "test-user",
):
    """
    Tạo Conversation dùng chung cho test.
    """

    service = ConversationService()

    conversation = service.create(
        title=title,
        user_id=user_id,
    )

    return service, conversation


# =========================================================
# 01
# =========================================================


def test_history_is_created_from_conversation():
    """
    Conversation phải tạo được ConversationHistory.
    """

    service, conversation = (
        create_conversation()
    )

    history = service.history(
        conversation.conversation_id
    )

    assert isinstance(
        history,
        ConversationHistory,
    )

    assert history.is_empty()


# =========================================================
# 02
# =========================================================


def test_user_message_is_available_in_memory():
    """
    User message phải được lưu vào memory.
    """

    service, conversation = (
        create_conversation()
    )

    service.add_user_message(
        conversation.conversation_id,
        "Chuyển đổi số là gì?",
    )

    history = service.history(
        conversation.conversation_id
    )

    messages = history.messages()

    assert len(messages) == 1

    assert (
        messages[0].content
        == "Chuyển đổi số là gì?"
    )

    assert messages[0].is_user()


# =========================================================
# 03
# =========================================================


def test_assistant_message_is_available_in_memory():
    """
    Assistant message phải được lưu vào memory.
    """

    service, conversation = (
        create_conversation()
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Chuyển đổi số là quá trình ứng dụng "
        "công nghệ số vào hoạt động quản lý.",
    )

    history = service.history(
        conversation.conversation_id
    )

    messages = history.messages()

    assert len(messages) == 1

    assert messages[0].is_assistant()

    assert (
        "Chuyển đổi số"
        in messages[0].content
    )


# =========================================================
# 04
# =========================================================


def test_system_message_is_available_in_memory():
    """
    System message phải được lưu đúng role.
    """

    service, conversation = (
        create_conversation()
    )

    service.add_system_message(
        conversation.conversation_id,
        "Bạn là trợ lý AI hành chính.",
    )

    message = (
        service.history(
            conversation.conversation_id
        )
        .messages()[0]
    )

    assert message.is_system()

    assert (
        message.content
        == "Bạn là trợ lý AI hành chính."
    )


# =========================================================
# 05
# =========================================================


def test_latest_returns_recent_messages():
    """
    latest() phải trả đúng N message gần nhất.
    """

    service, conversation = (
        create_conversation()
    )

    for index in range(5):
        service.add_user_message(
            conversation.conversation_id,
            f"Message {index}",
        )

    latest = (
        service.history(
            conversation.conversation_id
        )
        .latest(2)
    )

    assert len(latest) == 2

    assert (
        latest[0].content
        == "Message 3"
    )

    assert (
        latest[1].content
        == "Message 4"
    )


# =========================================================
# 06
# =========================================================


def test_latest_zero_returns_empty():
    """
    latest(0) phải trả danh sách rỗng.
    """

    service, conversation = (
        create_conversation()
    )

    service.add_user_message(
        conversation.conversation_id,
        "Hello",
    )

    latest = (
        service.history(
            conversation.conversation_id
        )
        .latest(0)
    )

    assert latest == []


# =========================================================
# 07
# =========================================================


def test_latest_negative_returns_empty():
    """
    latest() với limit âm phải an toàn.
    """

    service, conversation = (
        create_conversation()
    )

    service.add_user_message(
        conversation.conversation_id,
        "Hello",
    )

    latest = (
        service.history(
            conversation.conversation_id
        )
        .latest(-1)
    )

    assert latest == []


# =========================================================
# 08
# =========================================================


def test_history_to_prompt_contains_user_message():
    """
    Context prompt phải chứa User message.
    """

    service, conversation = (
        create_conversation()
    )

    service.add_user_message(
        conversation.conversation_id,
        "Nghị quyết 57 là gì?",
    )

    prompt = service.prompt(
        conversation.conversation_id
    )

    assert "USER:" in prompt

    assert (
        "Nghị quyết 57 là gì?"
        in prompt
    )


# =========================================================
# 09
# =========================================================


def test_history_to_prompt_contains_assistant_message():
    """
    Context prompt phải chứa Assistant message.
    """

    service, conversation = (
        create_conversation()
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Nghị quyết 57 nói về khoa học, "
        "công nghệ và chuyển đổi số.",
    )

    prompt = service.prompt(
        conversation.conversation_id
    )

    assert "ASSISTANT:" in prompt

    assert (
        "Nghị quyết 57"
        in prompt
    )


# =========================================================
# 10
# =========================================================


def test_history_to_prompt_preserves_message_order():
    """
    Prompt phải giữ nguyên thứ tự hội thoại.
    """

    service, conversation = (
        create_conversation()
    )

    service.add_user_message(
        conversation.conversation_id,
        "Câu hỏi thứ nhất",
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Trả lời thứ nhất",
    )

    service.add_user_message(
        conversation.conversation_id,
        "Câu hỏi thứ hai",
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Trả lời thứ hai",
    )

    prompt = service.prompt(
        conversation.conversation_id
    )

    position_q1 = prompt.index(
        "Câu hỏi thứ nhất"
    )

    position_a1 = prompt.index(
        "Trả lời thứ nhất"
    )

    position_q2 = prompt.index(
        "Câu hỏi thứ hai"
    )

    position_a2 = prompt.index(
        "Trả lời thứ hai"
    )

    assert (
        position_q1
        < position_a1
        < position_q2
        < position_a2
    )


# =========================================================
# 11
# =========================================================


def test_empty_history_produces_empty_prompt():
    """
    Conversation mới chưa có message phải có
    prompt/context rỗng.
    """

    service, conversation = (
        create_conversation()
    )

    prompt = service.prompt(
        conversation.conversation_id
    )

    assert prompt == ""


# =========================================================
# 12
# =========================================================


def test_memory_is_limited_by_max_messages():
    """
    ConversationHistory phải giới hạn số message.
    """

    service, conversation = (
        create_conversation()
    )

    history = service.history(
        conversation.conversation_id
    )

    history.max_messages = 3

    for index in range(5):
        history.add(
            ConversationMessage(
                role="user",
                content=f"Message {index}",
            )
        )

    messages = history.messages()

    assert len(messages) == 3

    assert (
        messages[0].content
        == "Message 2"
    )

    assert (
        messages[1].content
        == "Message 3"
    )

    assert (
        messages[2].content
        == "Message 4"
    )


# =========================================================
# 13
# =========================================================


def test_clear_memory_removes_context():
    """
    clear() phải xóa toàn bộ conversation memory.
    """

    service, conversation = (
        create_conversation()
    )

    service.add_user_message(
        conversation.conversation_id,
        "Thông tin cần xóa.",
    )

    assert (
        service.history(
            conversation.conversation_id
        ).count()
        == 1
    )

    service.clear(
        conversation.conversation_id
    )

    history = service.history(
        conversation.conversation_id
    )

    assert history.count() == 0

    assert history.is_empty()

    assert service.prompt(
        conversation.conversation_id
    ) == ""


# =========================================================
# 14
# =========================================================


def test_memory_isolated_between_conversations():
    """
    Hai Conversation khác nhau không được dùng chung memory.
    """

    service = ConversationService()

    conversation_a = service.create(
        title="Conversation A",
    )

    conversation_b = service.create(
        title="Conversation B",
    )

    service.add_user_message(
        conversation_a.conversation_id,
        "Thông tin của A",
    )

    service.add_user_message(
        conversation_b.conversation_id,
        "Thông tin của B",
    )

    prompt_a = service.prompt(
        conversation_a.conversation_id
    )

    prompt_b = service.prompt(
        conversation_b.conversation_id
    )

    assert "Thông tin của A" in prompt_a

    assert "Thông tin của B" not in prompt_a

    assert "Thông tin của B" in prompt_b

    assert "Thông tin của A" not in prompt_b


# =========================================================
# 15
# =========================================================


def test_multi_turn_context_contains_complete_recent_history():
    """
    Gate test của 13.5:

    Một cuộc hội thoại nhiều lượt phải tạo được
    context chứa đầy đủ lịch sử gần nhất theo đúng
    thứ tự User → Assistant → User → Assistant.
    """

    service, conversation = (
        create_conversation(
            title="Memory Gate Test",
            user_id="test-user",
        )
    )

    service.add_user_message(
        conversation.conversation_id,
        "Hành Chính AI là gì?",
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Hành Chính AI là trợ lý AI "
        "dành cho công tác hành chính.",
        provider="ollama",
        model="qwen3:8b",
    )

    service.add_user_message(
        conversation.conversation_id,
        "Nó hỗ trợ cán bộ như thế nào?",
    )

    service.add_assistant_message(
        conversation.conversation_id,
        "Hệ thống hỗ trợ tra cứu, "
        "soạn thảo và xử lý văn bản.",
        provider="ollama",
        model="qwen3:8b",
    )

    history = service.history(
        conversation.conversation_id
    )

    assert history.count() == 4

    prompt = service.prompt(
        conversation.conversation_id
    )

    assert (
        "Hành Chính AI là gì?"
        in prompt
    )

    assert (
        "Hành Chính AI là trợ lý AI"
        in prompt
    )

    assert (
        "Nó hỗ trợ cán bộ như thế nào?"
        in prompt
    )

    assert (
        "Hệ thống hỗ trợ tra cứu"
        in prompt
    )

    assert prompt.index(
        "Hành Chính AI là gì?"
    ) < prompt.index(
        "Nó hỗ trợ cán bộ như thế nào?"
    )

    assert prompt.index(
        "Nó hỗ trợ cán bộ như thế nào?"
    ) < prompt.index(
        "Hệ thống hỗ trợ tra cứu"
    )