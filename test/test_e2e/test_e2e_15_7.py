from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.api.routes.assistant import get_conversation_service


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _find_audio_file() -> Path:
    candidates = [
        PROJECT_ROOT / "voice_test.wav",
        PROJECT_ROOT / "test" / "voice_test.wav",
        PROJECT_ROOT / "tests" / "voice_test.wav",
        PROJECT_ROOT / "test" / "audio" / "voice_test.wav",
        PROJECT_ROOT / "tests" / "audio" / "voice_test.wav",
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    matches = list(PROJECT_ROOT.rglob("voice_test.wav"))

    for match in matches:
        if match.is_file():
            return match

    searched = "\n".join(
        f"  - {path}"
        for path in candidates
    )

    raise FileNotFoundError(
        "Không tìm thấy voice_test.wav trong project.\n"
        f"Project root: {PROJECT_ROOT}\n"
        "Đã kiểm tra:\n"
        f"{searched}"
    )


def _get_audio_file() -> Path:
    return _find_audio_file()


def _get_client() -> TestClient:
    return TestClient(app)


def _get_runtime_conversation_service():
    service = get_conversation_service()

    assert service is not None, (
        "ConversationService runtime chưa được khởi tạo."
    )

    return service


def _assert_voice_response(data: dict) -> None:
    required_fields = {
        "success",
        "conversation_id",
        "file_name",
        "transcript",
        "answer",
        "language",
        "duration",
        "citations",
        "metadata",
        "message",
    }

    missing = required_fields - set(data.keys())

    assert not missing, (
        "Thiếu field trong VoiceConversationResponse: "
        f"{sorted(missing)}"
    )

    assert data["success"] is True

    assert isinstance(
        data["conversation_id"],
        str,
    )
    assert data["conversation_id"]

    assert isinstance(
        data["file_name"],
        str,
    )
    assert data["file_name"]

    assert isinstance(
        data["transcript"],
        str,
    )
    assert data["transcript"].strip()

    assert isinstance(
        data["answer"],
        str,
    )
    assert data["answer"].strip()

    assert data["language"] == "vi"

    assert data["duration"] is not None
    assert data["duration"] > 0

    assert isinstance(
        data["citations"],
        list,
    )

    assert isinstance(
        data["metadata"],
        dict,
    )


def _post_voice_conversation(
    client: TestClient,
    conversation_id: str,
    audio_file: Path,
):
    with audio_file.open("rb") as audio:
        return client.post(
            "/voice/conversation",
            files={
                "file": (
                    audio_file.name,
                    audio,
                    "audio/wav",
                )
            },
            data={
                "conversation_id": conversation_id,
                "language": "vi",
            },
        )


def test_sprint_15_7_audio_file_exists() -> None:
    print("\n=== 15.7 AUDIO FILE CHECK ===")

    audio_file = _get_audio_file()

    assert audio_file.exists()
    assert audio_file.is_file()
    assert audio_file.stat().st_size > 0

    print(f"AUDIO FILE: {audio_file}")
    print(
        f"SIZE: {audio_file.stat().st_size} bytes"
    )
    print("AUDIO FILE: PASS")


def test_sprint_15_7_full_voice_ai_pipeline() -> None:
    print("\n=== 15.7 FULL VOICE AI PIPELINE ===")

    audio_file = _get_audio_file()
    client = _get_client()

    conversation_service = (
        _get_runtime_conversation_service()
    )

    conversation = conversation_service.create(
        title="Sprint 15.7 E2E Voice AI",
        user_id="test-user-15-7",
    )

    response = _post_voice_conversation(
        client=client,
        conversation_id=conversation.conversation_id,
        audio_file=audio_file,
    )

    print(
        f"STATUS: {response.status_code}"
    )
    print(
        f"RESPONSE: {response.text}"
    )

    assert response.status_code == 200

    data = response.json()

    _assert_voice_response(data)

    assert (
        data["conversation_id"]
        == conversation.conversation_id
    )

    metadata = data["metadata"]

    assert (
        metadata.get("pipeline_stage")
        == "voice_conversation"
    )

    assert (
        metadata.get("conversation_id")
        == conversation.conversation_id
    )

    assert (
        metadata.get("memory_enabled")
        is True
    )

    assert (
        metadata.get("history_used")
        is True
    )

    assert (
        metadata.get("history_message_count", 0)
        >= 2
    )

    voice_metadata = (
        metadata.get("voice_metadata", {})
    )

    assert (
        voice_metadata.get("engine")
        == "faster-whisper"
    )

    assert voice_metadata.get("model")
    assert voice_metadata.get("device")
    assert voice_metadata.get(
        "compute_type"
    )

    rag_result = metadata.get(
        "rag_result",
        {},
    )

    assert isinstance(
        rag_result,
        dict,
    )

    assert "question" in rag_result
    assert "answer" in rag_result

    print(
        f"TRANSCRIPT: {data['transcript']}"
    )

    print(
        f"ANSWER: {data['answer']}"
    )

    print(
        f"LANGUAGE: {data['language']}"
    )

    print(
        f"DURATION: {data['duration']}"
    )

    print(
        "MEMORY ENABLED: "
        f"{metadata.get('memory_enabled')}"
    )

    print(
        "HISTORY USED: "
        f"{metadata.get('history_used')}"
    )

    print(
        "HISTORY COUNT: "
        f"{metadata.get('history_message_count')}"
    )

    print(
        "VOICE ENGINE: "
        f"{voice_metadata.get('engine')}"
    )

    print(
        "VOICE MODEL: "
        f"{voice_metadata.get('model')}"
    )

    print(
        "RAG RESULT: "
        f"{json.dumps(rag_result, ensure_ascii=False)}"
    )

    print(
        "FULL VOICE AI PIPELINE: PASS"
    )


def test_sprint_15_7_conversation_persistence() -> None:
    print(
        "\n=== 15.7 CONVERSATION PERSISTENCE ==="
    )

    audio_file = _get_audio_file()
    client = _get_client()

    conversation_service = (
        _get_runtime_conversation_service()
    )

    conversation = conversation_service.create(
        title="Sprint 15.7 Persistence",
        user_id="test-user-15-7",
    )

    response = _post_voice_conversation(
        client=client,
        conversation_id=conversation.conversation_id,
        audio_file=audio_file,
    )

    assert response.status_code == 200

    data = response.json()

    _assert_voice_response(data)

    assert (
        data["conversation_id"]
        == conversation.conversation_id
    )

    stored = conversation_service.get(
        conversation.conversation_id
    )

    assert stored is not None

    # Conversation không có count().
    # Kiểm tra trực tiếp danh sách messages.
    assert len(stored.messages) == 2

    assert stored.messages[0].role == "user"

    assert (
        stored.messages[0].content
        == data["transcript"]
    )

    assert stored.messages[1].role == "assistant"

    assert (
        stored.messages[1].content
        == data["answer"]
    )

    print(
        f"CONVERSATION ID: "
        f"{conversation.conversation_id}"
    )

    print(
        f"MESSAGE COUNT: {len(stored.messages)}"
    )

    print(
        "USER MESSAGE: "
        f"{stored.messages[0].content}"
    )

    print(
        "ASSISTANT MESSAGE: "
        f"{stored.messages[1].content}"
    )

    print(
        "CONVERSATION PERSISTENCE: PASS"
    )


def test_sprint_15_7_contract_and_routes() -> None:
    print(
        "\n=== 15.7 CONTRACT AND ROUTES ==="
    )

    client = _get_client()

    openapi = client.get(
        "/openapi.json"
    )

    assert openapi.status_code == 200

    paths = openapi.json().get(
        "paths",
        {},
    )

    required_routes = {
        "/voice/upload",
        "/voice/ai",
        "/voice/document",
        "/voice/conversation",
    }

    missing = (
        required_routes
        - set(paths.keys())
    )

    assert not missing, (
        "Thiếu Voice route: "
        f"{sorted(missing)}"
    )

    conversation_route = paths[
        "/voice/conversation"
    ]

    assert "post" in conversation_route

    response_schema = (
        conversation_route["post"]
        .get("responses", {})
        .get("200", {})
    )

    assert response_schema

    print("VOICE ROUTES: PASS")
    print(
        "VOICE CONVERSATION POST: PASS"
    )
    print(
        "VOICE RESPONSE CONTRACT: PASS"
    )
    print(
        "CONTRACT AND ROUTES: PASS"
    )


def test_sprint_15_7_final_pipeline_metadata() -> None:
    print(
        "\n=== 15.7 FINAL PIPELINE METADATA ==="
    )

    audio_file = _get_audio_file()
    client = _get_client()

    conversation_service = (
        _get_runtime_conversation_service()
    )

    conversation = conversation_service.create(
        title="Sprint 15.7 Final Metadata",
        user_id="test-user-15-7",
    )

    response = _post_voice_conversation(
        client=client,
        conversation_id=conversation.conversation_id,
        audio_file=audio_file,
    )

    assert response.status_code == 200

    data = response.json()

    _assert_voice_response(data)

    metadata = data["metadata"]

    assert (
        metadata["pipeline_stage"]
        == "voice_conversation"
    )

    assert (
        metadata["conversation_id"]
        == conversation.conversation_id
    )

    assert (
        metadata["transcript"]
        == data["transcript"]
    )

    assert (
        metadata["file_name"]
        == data["file_name"]
    )

    assert (
        metadata["language"]
        == data["language"]
    )

    assert (
        metadata["voice_duration"]
        == data["duration"]
    )

    assert (
        metadata["memory_enabled"]
        is True
    )

    assert (
        metadata["history_used"]
        is True
    )

    assert (
        metadata["history_message_count"]
        >= 2
    )

    assert (
        metadata["voice_metadata"]["engine"]
        == "faster-whisper"
    )

    print("PIPELINE STAGE: PASS")
    print(
        "TRANSCRIPT METADATA: PASS"
    )
    print(
        "VOICE METADATA: PASS"
    )
    print(
        "MEMORY METADATA: PASS"
    )
    print(
        "FINAL PIPELINE METADATA: PASS"
    )


def test_sprint_15_7_summary() -> None:
    print(
        "\n=== 15.7 SUMMARY ==="
    )

    print("")
    print(
        "Các kiểm tra 15.7 được pytest "
        "đánh giá qua kết quả test."
    )
    print(
        "Nếu toàn bộ test PASS → "
        "Sprint 15.7 PASS."
    )
    print("")