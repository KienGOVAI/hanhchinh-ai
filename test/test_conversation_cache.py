"""
Tests for ConversationCache.

Sprint 13.1.3 - Chat Domain
Conversation Cache Layer
"""

from app.conversation.conversation import Conversation
from app.conversation.conversation_cache import ConversationCache


# ============================================================
# INIT
# ============================================================


def test_cache_initial_state():
    cache = ConversationCache()

    assert cache.count() == 0
    assert cache.list() == []


# ============================================================
# SET / GET
# ============================================================


def test_set_and_get_conversation():
    cache = ConversationCache()

    conversation = Conversation(
        conversation_id="conversation-001"
    )

    cache.set(conversation)

    result = cache.get(
        "conversation-001"
    )

    assert result is conversation


def test_get_missing_conversation_returns_none():
    cache = ConversationCache()

    result = cache.get(
        "conversation-does-not-exist"
    )

    assert result is None


def test_set_multiple_conversations():
    cache = ConversationCache()

    first = Conversation(
        conversation_id="conversation-001"
    )

    second = Conversation(
        conversation_id="conversation-002"
    )

    third = Conversation(
        conversation_id="conversation-003"
    )

    cache.set(first)
    cache.set(second)
    cache.set(third)

    assert cache.count() == 3

    assert cache.get(
        "conversation-001"
    ) is first

    assert cache.get(
        "conversation-002"
    ) is second

    assert cache.get(
        "conversation-003"
    ) is third


def test_set_same_id_replaces_conversation():
    cache = ConversationCache()

    first = Conversation(
        conversation_id="conversation-001",
        title="First",
    )

    second = Conversation(
        conversation_id="conversation-001",
        title="Second",
    )

    cache.set(first)
    cache.set(second)

    assert cache.count() == 1

    result = cache.get(
        "conversation-001"
    )

    assert result is second
    assert result.title == "Second"


# ============================================================
# EXISTS
# ============================================================


def test_exists_returns_false_for_missing_id():
    cache = ConversationCache()

    assert cache.exists(
        "conversation-does-not-exist"
    ) is False


def test_exists_returns_true_after_set():
    cache = ConversationCache()

    conversation = Conversation(
        conversation_id="conversation-001"
    )

    cache.set(conversation)

    assert cache.exists(
        "conversation-001"
    ) is True


def test_exists_returns_false_after_remove():
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


# ============================================================
# REMOVE
# ============================================================


def test_remove_conversation():
    cache = ConversationCache()

    conversation = Conversation(
        conversation_id="conversation-001"
    )

    cache.set(conversation)

    assert cache.count() == 1

    cache.remove(
        "conversation-001"
    )

    assert cache.count() == 0
    assert cache.get(
        "conversation-001"
    ) is None


def test_remove_missing_conversation_is_safe():
    cache = ConversationCache()

    cache.remove(
        "conversation-does-not-exist"
    )

    assert cache.count() == 0


def test_remove_one_keeps_other_conversations():
    cache = ConversationCache()

    first = Conversation(
        conversation_id="conversation-001"
    )

    second = Conversation(
        conversation_id="conversation-002"
    )

    cache.set(first)
    cache.set(second)

    cache.remove(
        "conversation-001"
    )

    assert cache.count() == 1
    assert cache.get(
        "conversation-001"
    ) is None

    assert cache.get(
        "conversation-002"
    ) is second


# ============================================================
# LIST
# ============================================================


def test_list_empty_cache():
    cache = ConversationCache()

    assert cache.list() == []


def test_list_returns_all_conversations():
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


def test_list_does_not_include_removed_conversation():
    cache = ConversationCache()

    first = Conversation(
        conversation_id="conversation-001"
    )

    second = Conversation(
        conversation_id="conversation-002"
    )

    cache.set(first)
    cache.set(second)

    cache.remove(
        "conversation-001"
    )

    conversations = cache.list()

    assert len(conversations) == 1
    assert second in conversations
    assert first not in conversations


# ============================================================
# COUNT
# ============================================================


def test_count_empty_cache():
    cache = ConversationCache()

    assert cache.count() == 0


def test_count_after_set():
    cache = ConversationCache()

    cache.set(
        Conversation(
            conversation_id="conversation-001"
        )
    )

    assert cache.count() == 1

    cache.set(
        Conversation(
            conversation_id="conversation-002"
        )
    )

    assert cache.count() == 2


def test_count_after_remove():
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

    cache.remove(
        "conversation-001"
    )

    assert cache.count() == 1


# ============================================================
# CLEAR
# ============================================================


def test_clear_empty_cache():
    cache = ConversationCache()

    cache.clear()

    assert cache.count() == 0
    assert cache.list() == []


def test_clear_cache():
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

    cache.set(
        Conversation(
            conversation_id="conversation-003"
        )
    )

    assert cache.count() == 3

    cache.clear()

    assert cache.count() == 0
    assert cache.list() == []


def test_clear_removes_all_accessible_conversations():
    cache = ConversationCache()

    ids = [
        "conversation-001",
        "conversation-002",
        "conversation-003",
        "conversation-004",
        "conversation-005",
    ]

    for conversation_id in ids:
        cache.set(
            Conversation(
                conversation_id=conversation_id
            )
        )

    assert cache.count() == 5

    cache.clear()

    for conversation_id in ids:
        assert cache.get(
            conversation_id
        ) is None

        assert cache.exists(
            conversation_id
        ) is False


# ============================================================
# OBJECT IDENTITY
# ============================================================


def test_cache_preserves_object_identity():
    cache = ConversationCache()

    conversation = Conversation(
        conversation_id="conversation-001",
        title="Test",
    )

    cache.set(conversation)

    result = cache.get(
        "conversation-001"
    )

    assert result is conversation


def test_cache_mutation_is_visible_through_get():
    cache = ConversationCache()

    conversation = Conversation(
        conversation_id="conversation-001",
        title="Original",
    )

    cache.set(conversation)

    conversation.title = "Updated"

    result = cache.get(
        "conversation-001"
    )

    assert result is conversation
    assert result.title == "Updated"


# ============================================================
# COMPLETE CACHE FLOW
# ============================================================


def test_complete_cache_flow():
    cache = ConversationCache()

    first = Conversation(
        conversation_id="conversation-001",
        title="Conversation 1",
    )

    second = Conversation(
        conversation_id="conversation-002",
        title="Conversation 2",
    )

    # Initially empty
    assert cache.count() == 0

    # Add
    cache.set(first)
    cache.set(second)

    assert cache.count() == 2

    # Exists
    assert cache.exists(
        "conversation-001"
    ) is True

    assert cache.exists(
        "conversation-002"
    ) is True

    # Get
    assert cache.get(
        "conversation-001"
    ) is first

    assert cache.get(
        "conversation-002"
    ) is second

    # List
    conversations = cache.list()

    assert len(conversations) == 2
    assert first in conversations
    assert second in conversations

    # Remove one
    cache.remove(
        "conversation-001"
    )

    assert cache.count() == 1
    assert cache.get(
        "conversation-001"
    ) is None

    assert cache.get(
        "conversation-002"
    ) is second

    # Clear remaining
    cache.clear()

    assert cache.count() == 0
    assert cache.list() == []