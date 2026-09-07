"""
Tests for ConversationMessage.

Sprint 13.1.5 - Chat Domain
Conversation Message Model
"""

import pytest

from app.conversation.conversation_message import (
    ConversationMessage,
)


# ============================================================
# BASIC CREATION
# ============================================================


def test_create_user_message():
    message = ConversationMessage(
        role="user",
        content="Xin chào",
    )

    assert message.role == "user"
    assert message.content == "Xin chào"


def test_create_assistant_message():
    message = ConversationMessage(
        role="assistant",
        content="Xin chào, tôi là Hành Chính AI.",
    )

    assert message.role == "assistant"
    assert (
        message.content
        == "Xin chào, tôi là Hành Chính AI."
    )


def test_create_system_message():
    message = ConversationMessage(
        role="system",
        content="Bạn là trợ lý hành chính.",
    )

    assert message.role == "system"
    assert (
        message.content
        == "Bạn là trợ lý hành chính."
    )


# ============================================================
# ROLE VALIDATION
# ============================================================


def test_valid_user_role():
    message = ConversationMessage(
        role="user",
        content="Xin chào",
    )

    assert message.is_user() is True


def test_valid_assistant_role():
    message = ConversationMessage(
        role="assistant",
        content="Xin chào",
    )

    assert message.is_assistant() is True


def test_valid_system_role():
    message = ConversationMessage(
        role="system",
        content="System prompt",
    )

    assert message.is_system() is True


def test_invalid_role_is_rejected():
    with pytest.raises(
        ValueError,
        match="Role không hợp lệ",
    ):
        ConversationMessage(
            role="invalid",
            content="Nội dung",
        )


def test_empty_role_is_rejected():
    with pytest.raises(
        ValueError,
        match="Role không hợp lệ",
    ):
        ConversationMessage(
            role="",
            content="Nội dung",
        )


def test_none_role_is_rejected():
    with pytest.raises(
        (ValueError, TypeError),
    ):
        ConversationMessage(
            role=None,
            content="Nội dung",
        )


# ============================================================
# CONTENT VALIDATION
# ============================================================


def test_content_must_be_string():
    with pytest.raises(
        TypeError,
        match="content phải là str",
    ):
        ConversationMessage(
            role="user",
            content=123,
        )


def test_none_content_is_rejected():
    with pytest.raises(
        TypeError,
        match="content phải là str",
    ):
        ConversationMessage(
            role="user",
            content=None,
        )


def test_empty_content_is_rejected():
    with pytest.raises(
        ValueError,
        match="content không được rỗng",
    ):
        ConversationMessage(
            role="user",
            content="",
        )


def test_whitespace_content_is_rejected():
    with pytest.raises(
        ValueError,
        match="content không được rỗng",
    ):
        ConversationMessage(
            role="user",
            content="   ",
        )


def test_newline_only_content_is_rejected():
    with pytest.raises(
        ValueError,
        match="content không được rỗng",
    ):
        ConversationMessage(
            role="user",
            content="\n\t",
        )


def test_valid_content_with_surrounding_spaces():
    message = ConversationMessage(
        role="user",
        content="  Xin chào  ",
    )

    assert message.content == "  Xin chào  "
    assert message.has_content() is True


# ============================================================
# ROLE HELPERS
# ============================================================


def test_user_message_helpers():
    message = ConversationMessage(
        role="user",
        content="Xin chào",
    )

    assert message.is_user() is True
    assert message.is_assistant() is False
    assert message.is_system() is False


def test_assistant_message_helpers():
    message = ConversationMessage(
        role="assistant",
        content="Xin chào",
    )

    assert message.is_user() is False
    assert message.is_assistant() is True
    assert message.is_system() is False


def test_system_message_helpers():
    message = ConversationMessage(
        role="system",
        content="System",
    )

    assert message.is_user() is False
    assert message.is_assistant() is False
    assert message.is_system() is True


# ============================================================
# HAS CONTENT
# ============================================================


def test_has_content_returns_true():
    message = ConversationMessage(
        role="user",
        content="Xin chào",
    )

    assert message.has_content() is True


def test_has_content_ignores_surrounding_whitespace():
    message = ConversationMessage(
        role="user",
        content="   Xin chào   ",
    )

    assert message.has_content() is True


# ============================================================
# METADATA
# ============================================================


def test_default_metadata():
    message = ConversationMessage(
        role="user",
        content="Xin chào",
    )

    assert message.model == ""
    assert message.provider == ""
    assert message.tokens == 0
    assert message.error is False


def test_provider_metadata():
    message = ConversationMessage(
        role="assistant",
        content="Nội dung trả lời",
        provider="ollama",
    )

    assert message.provider == "ollama"


def test_model_metadata():
    message = ConversationMessage(
        role="assistant",
        content="Nội dung trả lời",
        model="qwen3:8b",
    )

    assert message.model == "qwen3:8b"


def test_tokens_metadata():
    message = ConversationMessage(
        role="assistant",
        content="Nội dung trả lời",
        tokens=512,
    )

    assert message.tokens == 512


def test_error_metadata():
    message = ConversationMessage(
        role="assistant",
        content="Có lỗi xảy ra",
        error=True,
    )

    assert message.error is True


def test_complete_metadata():
    message = ConversationMessage(
        role="assistant",
        content="Kết quả trả lời",
        model="qwen3:8b",
        provider="ollama",
        tokens=1024,
        error=False,
    )

    assert message.model == "qwen3:8b"
    assert message.provider == "ollama"
    assert message.tokens == 1024
    assert message.error is False


# ============================================================
# CREATED_AT
# ============================================================


def test_created_at_is_generated():
    message = ConversationMessage(
        role="user",
        content="Xin chào",
    )

    assert message.created_at is not None


def test_created_at_can_be_provided():
    from datetime import datetime

    timestamp = datetime(
        2026,
        8,
        11,
        10,
        30,
    )

    message = ConversationMessage(
        role="user",
        content="Xin chào",
        created_at=timestamp,
    )

    assert message.created_at == timestamp


# ============================================================
# PREVIEW
# ============================================================


def test_preview_returns_original_short_content():
    message = ConversationMessage(
        role="user",
        content="Xin chào",
    )

    assert message.preview() == "Xin chào"


def test_preview_strips_surrounding_whitespace():
    message = ConversationMessage(
        role="user",
        content="   Xin chào   ",
    )

    assert message.preview() == "Xin chào"


def test_preview_long_content_is_truncated():
    content = "A" * 100

    message = ConversationMessage(
        role="user",
        content=content,
    )

    preview = message.preview(80)

    assert preview.endswith("...")
    assert preview == ("A" * 80) + "..."


def test_preview_exact_length_is_not_truncated():
    content = "A" * 80

    message = ConversationMessage(
        role="user",
        content=content,
    )

    preview = message.preview(80)

    assert preview == content
    assert not preview.endswith("...")


def test_preview_short_custom_length():
    message = ConversationMessage(
        role="user",
        content="ABCDEFGHIJ",
    )

    preview = message.preview(5)

    assert preview == "ABCDE..."


def test_preview_zero_length():
    message = ConversationMessage(
        role="user",
        content="Xin chào",
    )

    preview = message.preview(0)

    # preview() hiện tại trả về text[:0] khi
    # length = 0 và nội dung không rỗng.
    assert preview == ""


# ============================================================
# UNICODE / VIETNAMESE
# ============================================================


def test_vietnamese_content():
    content = (
        "Công văn về chuyển đổi số "
        "và cải cách hành chính."
    )

    message = ConversationMessage(
        role="user",
        content=content,
    )

    assert message.content == content
    assert message.has_content() is True


def test_unicode_preview():
    content = (
        "Cải cách hành chính và chuyển đổi số "
        "tại xã Yên Minh."
    )

    message = ConversationMessage(
        role="user",
        content=content,
    )

    preview = message.preview(10)

    # 10 ký tự đầu tiên của chuỗi là:
    # "Cải cách h"
    assert preview == "Cải cách h..."


# ============================================================
# ERROR MESSAGE
# ============================================================


def test_error_message_can_be_marked():
    message = ConversationMessage(
        role="assistant",
        content="Không thể xử lý yêu cầu.",
        error=True,
    )

    assert message.error is True
    assert message.is_assistant() is True


def test_normal_message_is_not_error():
    message = ConversationMessage(
        role="assistant",
        content="Đã xử lý yêu cầu.",
    )

    assert message.error is False


# ============================================================
# OBJECT INDEPENDENCE
# ============================================================


def test_messages_are_independent():
    first = ConversationMessage(
        role="user",
        content="Message 1",
    )

    second = ConversationMessage(
        role="user",
        content="Message 2",
    )

    assert first is not second
    assert first.content != second.content


def test_message_metadata_is_independent():
    first = ConversationMessage(
        role="assistant",
        content="First",
        provider="ollama",
    )

    second = ConversationMessage(
        role="assistant",
        content="Second",
        provider="openai",
    )

    assert first.provider == "ollama"
    assert second.provider == "openai"


# ============================================================
# COMPLETE MESSAGE CONTRACT
# ============================================================


def test_complete_user_message_contract():
    message = ConversationMessage(
        role="user",
        content="Hãy soạn công văn về chuyển đổi số.",
    )

    assert message.role == "user"
    assert message.is_user() is True
    assert message.is_assistant() is False
    assert message.is_system() is False
    assert message.has_content() is True

    assert message.model == ""
    assert message.provider == ""
    assert message.tokens == 0
    assert message.error is False
    assert message.created_at is not None


def test_complete_assistant_message_contract():
    message = ConversationMessage(
        role="assistant",
        content="Tôi sẽ hỗ trợ soạn công văn.",
        provider="ollama",
        model="qwen3:8b",
        tokens=256,
    )

    assert message.role == "assistant"
    assert message.is_user() is False
    assert message.is_assistant() is True
    assert message.is_system() is False
    assert message.has_content() is True

    assert message.provider == "ollama"
    assert message.model == "qwen3:8b"
    assert message.tokens == 256
    assert message.error is False
    assert message.created_at is not None


def test_complete_system_message_contract():
    message = ConversationMessage(
        role="system",
        content="Bạn là trợ lý AI hành chính.",
    )

    assert message.role == "system"
    assert message.is_user() is False
    assert message.is_assistant() is False
    assert message.is_system() is True
    assert message.has_content() is True


# ============================================================
# VALIDATION CONTRACT
# ============================================================


def test_invalid_role_does_not_create_message():
    with pytest.raises(
        ValueError,
        match="Role không hợp lệ",
    ):
        ConversationMessage(
            role="admin",
            content="Nội dung",
        )


def test_invalid_content_does_not_create_message():
    with pytest.raises(
        ValueError,
        match="content không được rỗng",
    ):
        ConversationMessage(
            role="user",
            content=" ",
        )