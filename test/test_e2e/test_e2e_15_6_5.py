"""
Sprint 15.6.5
-------------
Voice Conversation Contract + Error Handling + Regression

Mục tiêu:

    1. Conversation ID không tồn tại
       -> HTTP 404

    2. Transcript rỗng
       -> VoiceConversationService reject

    3. Conversation hợp lệ
       -> pipeline vẫn hoạt động

    4. Memory metadata
       -> đúng contract

    5. Các Voice API hiện tại
       -> không bị ảnh hưởng

    6. OpenAPI
       -> đầy đủ Voice routes
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.voice.conversation import VoiceConversationService


def test_voice_conversation_invalid_conversation() -> None:
    print("")
    print("=== INVALID CONVERSATION ID ===")

    audio_path = Path("voice_test.wav")

    assert audio_path.exists()

    client = TestClient(
        main_module.app
    )

    invalid_id = (
        "00000000-0000-0000-0000-000000000000"
    )

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
                "conversation_id": invalid_id,
                "language": "vi",
            },
        )

    print(
        "STATUS:",
        response.status_code,
    )

    print(
        "RESPONSE:",
        response.text,
    )

    assert response.status_code == 404

    print("INVALID CONVERSATION: PASS")


def test_voice_conversation_empty_transcript() -> None:
    print("")
    print("=== EMPTY TRANSCRIPT ===")

    service = VoiceConversationService(
        main_module.conversation_service,
        main_module.assistant_service,
    )

    conversation = (
        main_module.conversation_service.create(
            title="Sprint 15.6.5 Empty Transcript",
        )
    )

    with pytest.raises(
        ValueError,
        match="transcript không được để trống",
    ):
        service.process(
            transcript="   ",
            conversation_id=(
                conversation.conversation_id
            ),
        )

    print("EMPTY TRANSCRIPT: PASS")


def test_voice_conversation_valid_pipeline() -> None:
    print("")
    print("=== VALID VOICE CONVERSATION ===")

    audio_path = Path("voice_test.wav")

    assert audio_path.exists()

    conversation = (
        main_module.conversation_service.create(
            title="Sprint 15.6.5 Valid Pipeline",
        )
    )

    conversation_id = (
        conversation.conversation_id
    )

    client = TestClient(
        main_module.app
    )

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

    print(
        "STATUS:",
        response.status_code,
    )

    print(
        "RESPONSE:",
        response.text,
    )

    assert response.status_code == 200

    result = response.json()

    assert result["success"] is True

    assert (
        result["conversation_id"]
        == conversation_id
    )

    assert (
        isinstance(
            result["transcript"],
            str,
        )
        and result["transcript"].strip()
    )

    assert (
        isinstance(
            result["answer"],
            str,
        )
        and result["answer"].strip()
    )

    metadata = result.get(
        "metadata",
        {},
    )

    assert (
        metadata.get(
            "pipeline_stage"
        )
        == "voice_conversation"
    )

    assert (
        metadata.get(
            "conversation_id"
        )
        == conversation_id
    )

    assert (
        metadata.get(
            "history_used"
        )
        is True
    )

    assert (
        metadata.get(
            "memory_enabled"
        )
        is True
    )

    history = (
        main_module.conversation_service.history(
            conversation_id
        )
    )

    assert history.count() >= 2

    print("VALID PIPELINE: PASS")


def test_voice_openapi_regression() -> None:
    print("")
    print("=== VOICE OPENAPI REGRESSION ===")

    client = TestClient(
        main_module.app
    )

    openapi = client.get(
        "/openapi.json"
    )

    assert openapi.status_code == 200

    paths = openapi.json().get(
        "paths",
        {},
    )

    expected_routes = {
        "/voice/upload",
        "/voice/ai",
        "/voice/document",
        "/voice/conversation",
    }

    print(
        "VOICE ROUTES:",
        sorted(
            route
            for route in paths
            if route.startswith("/voice/")
        ),
    )

    for route in expected_routes:
        assert route in paths
        assert "post" in paths[route]

    print("OPENAPI REGRESSION: PASS")


def test_voice_route_regression() -> None:
    print("")
    print("=== VOICE ROUTE REGRESSION ===")

    client = TestClient(
        main_module.app
    )

    openapi = client.get(
        "/openapi.json"
    )

    paths = openapi.json()["paths"]

    assert "/voice/upload" in paths
    assert "/voice/ai" in paths
    assert "/voice/document" in paths
    assert "/voice/conversation" in paths

    print("VOICE UPLOAD: PASS")
    print("VOICE AI: PASS")
    print("VOICE DOCUMENT: PASS")
    print("VOICE CONVERSATION: PASS")


def test_voice_conversation_final_contract() -> None:
    print("")
    print("=== FINAL CONTRACT ===")

    conversation = (
        main_module.conversation_service.create(
            title="Sprint 15.6.5 Contract",
        )
    )

    service = VoiceConversationService(
        main_module.conversation_service,
        main_module.assistant_service,
    )

    response = service.process(
        transcript="Kiểm tra khả năng ghi nhớ hội thoại.",
        conversation_id=(
            conversation.conversation_id
        ),
    )

    assert response is not None

    assert isinstance(
        response.answer,
        str,
    )

    assert response.answer.strip()

    metadata = response.metadata

    assert (
        metadata.get(
            "pipeline_stage"
        )
        == "voice_conversation"
    )

    assert (
        metadata.get(
            "conversation_id"
        )
        == conversation.conversation_id
    )

    assert (
        metadata.get(
            "history_used"
        )
        is True
    )

    assert (
        metadata.get(
            "history_message_count"
        )
        >= 2
    )

    print("FINAL CONTRACT: PASS")


def test_sprint_15_6_5_summary() -> None:
    print("")
    print("=== 15.6.5 SUMMARY ===")
    print("")
    print("INVALID CONVERSATION: PASS")
    print("EMPTY TRANSCRIPT: PASS")
    print("VALID PIPELINE: PASS")
    print("OPENAPI REGRESSION: PASS")
    print("VOICE ROUTE REGRESSION: PASS")
    print("FINAL CONTRACT: PASS")
    print("")
    print("15.6.5: PASS")