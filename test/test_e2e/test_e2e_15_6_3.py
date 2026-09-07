"""
Sprint 15.6.3
-------------
E2E Voice + Conversation + Memory + AI

Pipeline:

    Audio
      ↓
    Voice Engine
      ↓
    Transcript
      ↓
    Conversation
      ↓
    Conversation History
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


def test_e2e_voice_conversation_memory() -> None:
    print("")
    print("=== CREATE CONVERSATION ===")

    conversation = main_module.conversation_service.create(
        title="Sprint 15.6.3 E2E",
    )

    conversation_id = conversation.conversation_id

    print("CONVERSATION ID:", conversation_id)

    audio_path = Path("voice_test.wav")

    assert audio_path.exists(), (
        f"Không tìm thấy file audio: "
        f"{audio_path.resolve()}"
    )

    client = TestClient(main_module.app)

    print("")
    print("=== SEND VOICE MESSAGE ===")

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

    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)

    assert response.status_code == 200

    result = response.json()

    print("")
    print("=== RESPONSE CONTRACT ===")

    print("SUCCESS:", result.get("success"))
    print(
        "CONVERSATION ID:",
        result.get("conversation_id"),
    )
    print("FILE:", result.get("file_name"))
    print("TRANSCRIPT:", result.get("transcript"))
    print("ANSWER:", result.get("answer"))
    print("LANGUAGE:", result.get("language"))
    print("DURATION:", result.get("duration"))

    assert result["success"] is True

    assert (
        result["conversation_id"]
        == conversation_id
    )

    assert isinstance(
        result["transcript"],
        str,
    )

    assert result["transcript"].strip()

    assert isinstance(
        result["answer"],
        str,
    )

    assert result["answer"].strip()

    metadata = result.get(
        "metadata",
        {},
    )

    print("")
    print("=== MEMORY CONTRACT ===")

    print(
        "PIPELINE:",
        metadata.get("pipeline_stage"),
    )

    print(
        "HISTORY COUNT:",
        metadata.get(
            "history_message_count"
        ),
    )

    print(
        "HISTORY USED:",
        metadata.get("history_used"),
    )

    print(
        "MEMORY ENABLED:",
        metadata.get("memory_enabled"),
    )

    assert (
        metadata.get("pipeline_stage")
        == "voice_conversation"
    )

    assert (
        metadata.get("conversation_id")
        == conversation_id
    )

    assert (
        metadata.get("history_used")
        is True
    )

    print("")
    print("=== CONVERSATION STATE ===")

    history = (
        main_module.conversation_service.history(
            conversation_id
        )
    )

    print(
        "MESSAGE COUNT:",
        history.count(),
    )

    print("HISTORY:")
    print(history.to_prompt())

    assert history.count() >= 2

    print("")
    print("=== 15.6.3 E2E CHECK ===")
    print("")
    print("15.6.3 E2E: PASS")
    print(
        "VOICE -> TRANSCRIPT -> "
        "CONVERSATION -> MEMORY -> "
        "AI -> ASSISTANT: PASS"
    )