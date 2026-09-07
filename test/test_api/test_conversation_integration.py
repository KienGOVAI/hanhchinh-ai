"""Sprint 13.3 - Conversation Integration."""
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
import app.api.routes.assistant as assistant_route
from app.main import app
from app.conversation.conversation_service import ConversationService

client = TestClient(app)

class FakeAssistantService:
    def __init__(self) -> None:
        self.call_count = 0
        self.questions: list[str] = []
        self.answer_text = "Nghị quyết 57 tập trung vào khoa học, công nghệ, đổi mới sáng tạo và chuyển đổi số."
    def answer(self, question: str):
        self.call_count += 1
        self.questions.append(question)
        return SimpleNamespace(
            answer=self.answer_text, query=question, citations=[],
            metadata={"provider": "ollama", "model": "qwen3:8b", "pipeline_stage": "citation", "retrieved_count": 0, "citation_count": 0},
        )

@pytest.fixture
def runtime():
    original_assistant = assistant_route._assistant_service
    original_conversation = assistant_route._conversation_service
    assistant_service = FakeAssistantService()
    conversation_service = ConversationService()
    assistant_route.configure_assistant_service(assistant_service)
    assistant_route.configure_conversation_service(conversation_service)
    yield assistant_service, conversation_service
    assistant_route._assistant_service = original_assistant
    assistant_route._conversation_service = original_conversation

def test_conversation_can_be_created(runtime):
    _, service = runtime
    c = service.create(title="Chat Test", user_id="test-user")
    assert c.conversation_id
    assert c.title == "Chat Test"
    assert c.user_id == "test-user"
    assert c.message_count() == 0

def test_chat_api_accepts_conversation_id(runtime):
    ai, service = runtime
    c = service.create()
    r = client.post("/assistant/ask", json={"question": "Nghị quyết 57 nói gì?", "conversation_id": c.conversation_id})
    assert r.status_code == 200
    assert ai.call_count == 1

def test_user_message_is_saved_to_conversation(runtime):
    _, service = runtime
    c = service.create(); q = "Chuyển đổi số là gì?"
    r = client.post("/assistant/ask", json={"question": q, "conversation_id": c.conversation_id})
    assert r.status_code == 200
    messages = service.history(c.conversation_id).messages()
    users = [m for m in messages if m.is_user()]
    assert len(users) == 1
    assert users[0].content == q

def test_assistant_message_is_saved_to_conversation(runtime):
    ai, service = runtime
    c = service.create()
    r = client.post("/assistant/ask", json={"question": "Hỏi thử.", "conversation_id": c.conversation_id})
    assert r.status_code == 200
    assistants = [m for m in service.history(c.conversation_id).messages() if m.is_assistant()]
    assert len(assistants) == 1
    assert assistants[0].content == ai.answer_text

def test_conversation_message_order(runtime):
    ai, service = runtime
    c = service.create(); q = "Hãy giải thích RAG."
    r = client.post("/assistant/ask", json={"question": q, "conversation_id": c.conversation_id})
    assert r.status_code == 200
    messages = service.history(c.conversation_id).messages()
    assert len(messages) == 2
    assert messages[0].role == "user" and messages[0].content == q
    assert messages[1].role == "assistant" and messages[1].content == ai.answer_text

def test_multi_turn_conversation(runtime):
    ai, service = runtime
    c = service.create(); q1 = "Nghị quyết 57 nói về gì?"; q2 = "Vậy cấp xã cần làm gì?"
    r1 = client.post("/assistant/ask", json={"question": q1, "conversation_id": c.conversation_id})
    r2 = client.post("/assistant/ask", json={"question": q2, "conversation_id": c.conversation_id})
    assert r1.status_code == 200 and r2.status_code == 200
    assert ai.call_count == 2
    messages = service.history(c.conversation_id).messages()
    assert len(messages) == 4
    assert messages[0].role == "user" and messages[0].content == q1
    assert messages[1].role == "assistant"
    assert messages[2].role == "user" and messages[2].content == q2
    assert messages[3].role == "assistant"

def test_conversation_history_can_be_converted_to_prompt(runtime):
    _, service = runtime
    c = service.create()
    service.add_user_message(c.conversation_id, "Nghị quyết 57 nói về gì?")
    service.add_assistant_message(c.conversation_id, "Nghị quyết 57 liên quan đến khoa học, công nghệ và chuyển đổi số.")
    service.add_user_message(c.conversation_id, "Vậy cấp xã cần làm gì?")
    prompt = service.prompt(c.conversation_id)
    assert "USER:" in prompt and "ASSISTANT:" in prompt
    assert "Nghị quyết 57 nói về gì?" in prompt
    assert "khoa học, công nghệ" in prompt
    assert "Vậy cấp xã cần làm gì?" in prompt

def test_conversations_are_isolated(runtime):
    _, service = runtime
    a = service.create(title="Conversation A"); b = service.create(title="Conversation B")
    service.add_user_message(a.conversation_id, "Nội dung A")
    service.add_user_message(b.conversation_id, "Nội dung B")
    ha = service.history(a.conversation_id); hb = service.history(b.conversation_id)
    assert ha.count() == 1 and hb.count() == 1
    assert ha.messages()[0].content == "Nội dung A"
    assert hb.messages()[0].content == "Nội dung B"

def test_conversation_can_be_cleared(runtime):
    _, service = runtime
    c = service.create()
    service.add_user_message(c.conversation_id, "Xin chào")
    service.add_assistant_message(c.conversation_id, "Xin chào, tôi là Hành Chính AI.")
    assert service.history(c.conversation_id).count() == 2
    service.clear(c.conversation_id)
    assert service.history(c.conversation_id).count() == 0

def test_chat_api_still_works_without_conversation_id(runtime):
    ai, _ = runtime
    r = client.post("/assistant/ask", json={"question": "Chuyển đổi số là gì?"})
    assert r.status_code == 200
    assert ai.call_count == 1

def test_invalid_conversation_id_is_rejected(runtime):
    r = client.post("/assistant/ask", json={"question": "Hỏi thử.", "conversation_id": "conversation-does-not-exist"})
    assert r.status_code == 404

def test_final_conversation_integration_gate(runtime):
    ai, service = runtime
    c = service.create(title="Final Integration Test", user_id="test-user")
    q1 = "Hãy giới thiệu Hành Chính AI."; q2 = "Nó hỗ trợ cán bộ như thế nào?"
    r1 = client.post("/assistant/ask", json={"question": q1, "conversation_id": c.conversation_id})
    r2 = client.post("/assistant/ask", json={"question": q2, "conversation_id": c.conversation_id})
    assert r1.status_code == 200 and r2.status_code == 200
    assert ai.call_count == 2
    messages = service.history(c.conversation_id).messages()
    assert len(messages) == 4
    assert messages[0].role == "user" and messages[0].content == q1
    assert messages[1].role == "assistant"
    assert messages[2].role == "user" and messages[2].content == q2
    assert messages[3].role == "assistant"
    prompt = service.prompt(c.conversation_id)
    assert q1 in prompt and q2 in prompt
    assert "Hành Chính AI" in prompt
    assert "hỗ trợ cán bộ" in prompt
