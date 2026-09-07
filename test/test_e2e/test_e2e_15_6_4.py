"""
Sprint 15.6.4
-------------
Multi-turn Voice Conversation Memory E2E

Mục tiêu:

    Voice #1
        ↓
    Conversation
        ↓
    Memory

    Voice #2
        ↓
    Cùng Conversation
        ↓
    Memory được sử dụng
        ↓
    AI hiểu context của lượt trước

Pipeline:

    Audio
      ↓
    Voice Engine
      ↓
    Transcript
      ↓
    Conversation
      ↓
    History
      ↓
    Assistant + Memory
      ↓
    Assistant Response
      ↓
    Save Assistant Message
"""

from pathlib import Path

from fastapi.testclient import TestClient

import app.main as main_module


def _send_voice(
    client: TestClient,
    conversation_id: str,
    audio_path: Path,
):
    with audio_path.open("rb") as audio_file:
        response = client.post(
            "/voice/conversation",
            files={
                "file": (
                    audio_path.name,
                    audio_file,
                    "audio/wav",
                )
            },
            data={
                "conversation_id": conversation_id,
                "language": "vi",
            },
        )

    return response


def test_e2e_multi_turn_voice_memory() -> None:
    print("")
    print("=== 15.6.4 MULTI-TURN VOICE MEMORY ===")

    audio_path = Path("voice_test.wav")

    assert audio_path.exists(), (
        f"Không tìm thấy file audio: "
        f"{audio_path.resolve()}"
    )

    print("")
    print("=== CREATE CONVERSATION ===")

    conversation = (
        main_module.conversation_service.create(
            title="Sprint 15.6.4 Multi Turn",
        )
    )

    conversation_id = conversation.conversation_id

    print(
        "CONVERSATION ID:",
        conversation_id,
    )

    client = TestClient(
        main_module.app
    )

    # =========================================================
    # TURN 1
    # =========================================================

    print("")
    print("=== TURN 1 ===")

    response_1 = _send_voice(
        client,
        conversation_id,
        audio_path,
    )

    print(
        "TURN 1 STATUS:",
        response_1.status_code,
    )

    print(
        "TURN 1 RESPONSE:",
        response_1.text,
    )

    assert response_1.status_code == 200

    result_1 = response_1.json()

    assert result_1["success"] is True

    assert (
        result_1["conversation_id"]
        == conversation_id
    )

    assert (
        isinstance(
            result_1["transcript"],
            str,
        )
        and result_1["transcript"].strip()
    )

    assert (
        isinstance(
            result_1["answer"],
            str,
        )
        and result_1["answer"].strip()
    )

    metadata_1 = result_1.get(
        "metadata",
        {},
    )

    print("")
    print("TURN 1 MEMORY:")
    print(
        "HISTORY COUNT:",
        metadata_1.get(
            "history_message_count"
        ),
    )
    print(
        "HISTORY USED:",
        metadata_1.get(
            "history_used"
        ),
    )
    print(
        "MEMORY ENABLED:",
        metadata_1.get(
            "memory_enabled"
        ),
    )

    assert (
        metadata_1.get(
            "pipeline_stage"
        )
        == "voice_conversation"
    )

    assert (
        metadata_1.get(
            "conversation_id"
        )
        == conversation_id
    )

    assert (
        metadata_1.get(
            "history_used"
        )
        is True
    )

    # =========================================================
    # STATE AFTER TURN 1
    # =========================================================

    history_after_1 = (
        main_module.conversation_service.history(
            conversation_id
        )
    )

    print("")
    print("=== STATE AFTER TURN 1 ===")
    print(
        "MESSAGE COUNT:",
        history_after_1.count(),
    )

    print("HISTORY:")
    print(
        history_after_1.to_prompt()
    )

    assert (
        history_after_1.count()
        >= 2
    )

    # =========================================================
    # TURN 2
    # =========================================================

    print("")
    print("=== TURN 2 ===")

    response_2 = _send_voice(
        client,
        conversation_id,
        audio_path,
    )

    print(
        "TURN 2 STATUS:",
        response_2.status_code,
    )

    print(
        "TURN 2 RESPONSE:",
        response_2.text,
    )

    assert response_2.status_code == 200

    result_2 = response_2.json()

    assert result_2["success"] is True

    assert (
        result_2["conversation_id"]
        == conversation_id
    )

    assert (
        isinstance(
            result_2["transcript"],
            str,
        )
        and result_2["transcript"].strip()
    )

    assert (
        isinstance(
            result_2["answer"],
            str,
        )
        and result_2["answer"].strip()
    )

    metadata_2 = result_2.get(
        "metadata",
        {},
    )

    print("")
    print("TURN 2 MEMORY:")
    print(
        "HISTORY COUNT:",
        metadata_2.get(
            "history_message_count"
        ),
    )
    print(
        "HISTORY USED:",
        metadata_2.get(
            "history_used"
        ),
    )
    print(
        "MEMORY ENABLED:",
        metadata_2.get(
            "memory_enabled"
        ),
    )

    assert (
        metadata_2.get(
            "pipeline_stage"
        )
        == "voice_conversation"
    )

    assert (
        metadata_2.get(
            "conversation_id"
        )
        == conversation_id
    )

    assert (
        metadata_2.get(
            "history_used"
        )
        is True
    )

    # =========================================================
    # MEMORY GROWTH
    # =========================================================

    history_count_1 = metadata_1.get(
        "history_message_count"
    )

    history_count_2 = metadata_2.get(
        "history_message_count"
    )

    assert isinstance(
        history_count_1,
        int,
    )

    assert isinstance(
        history_count_2,
        int,
    )

    assert (
        history_count_2
        > history_count_1
    )

    print("")
    print(
        "MEMORY GROWTH:",
        history_count_1,
        "->",
        history_count_2,
    )

    # =========================================================
    # FINAL CONVERSATION STATE
    # =========================================================

    final_history = (
        main_module.conversation_service.history(
            conversation_id
        )
    )

    print("")
    print("=== FINAL CONVERSATION STATE ===")

    final_count = final_history.count()

    print(
        "FINAL MESSAGE COUNT:",
        final_count,
    )

    print("FINAL HISTORY:")
    print(
        final_history.to_prompt()
    )

    # Hai lượt Voice:
    #
    # USER
    # ASSISTANT
    # USER
    # ASSISTANT
    #
    # => tối thiểu 4 message.

    assert final_count >= 4

    # ConversationHistory.messages()
    # là method, không phải property.

    messages = final_history.messages()

    assert len(messages) >= 4

    assert messages[0].is_user()
    assert messages[1].is_assistant()
    assert messages[2].is_user()
    assert messages[3].is_assistant()

    # =========================================================
    # SAME CONVERSATION
    # =========================================================

    assert (
        result_1["conversation_id"]
        == result_2["conversation_id"]
        == conversation_id
    )

    print("")
    print("=== 15.6.4 E2E CHECK ===")
    print("")
    print("TURN 1: PASS")
    print("TURN 2: PASS")
    print("SAME CONVERSATION: PASS")
    print("MEMORY GROWTH: PASS")
    print("MULTI-TURN HISTORY: PASS")
    print("MESSAGE ORDER: PASS")
    print("")
    print("15.6.4 E2E: PASS")
    print(
        "VOICE -> CONVERSATION -> "
        "MEMORY -> CONTEXT -> AI: PASS"
    )