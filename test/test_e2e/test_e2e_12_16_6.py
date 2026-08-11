"""
12.16.6 - E2E Complete User Journey.

Mục tiêu:
    Kiểm tra một hành trình sử dụng hoàn chỉnh của người dùng
    từ Application → Knowledge → Assistant → Citation.

User Journey:

    User
      ↓
    Application
      ↓
    Knowledge Search
      ↓
    Knowledge Results
      ↓
    Assistant Question
      ↓
    Answer
      ↓
    Citation
      ↓
    Metadata
      ↓
    Follow-up Question

Phạm vi:
    - Application availability
    - Knowledge search
    - Knowledge result
    - Assistant question
    - Assistant answer
    - Citation
    - Metadata
    - Follow-up question
    - Runtime continuity

Không thay đổi production code.
"""

from __future__ import annotations

import os


# =========================================================
# TEST ENVIRONMENT
# =========================================================

# Phải bật trước khi import app.main.
os.environ["KNOWLEDGE_DEMO_MODE"] = "true"


# =========================================================
# FASTAPI
# =========================================================

from fastapi.testclient import TestClient


# =========================================================
# APPLICATION
# =========================================================

from app.main import app


# =========================================================
# CLIENT
# =========================================================

client = TestClient(app)


# =========================================================
# CONSTANTS
# =========================================================

KNOWLEDGE_ENDPOINT = "/knowledge/search"

ASSISTANT_ENDPOINT = "/assistant/ask"

KNOWLEDGE_QUERY = "Chuyển đổi số"

ASSISTANT_QUESTION = "Chuyển đổi số là gì?"

FOLLOW_UP_QUESTION = (
    "Triển khai chuyển đổi số "
    "cần gắn với những nội dung nào?"
)

QUERY_VECTOR = [
    1.0,
    0.0,
    0.0,
]


# =========================================================
# HELPERS
# =========================================================

def search_knowledge(
    query: str = KNOWLEDGE_QUERY,
):
    """
    Gửi request tới Knowledge API.
    """

    return client.post(
        KNOWLEDGE_ENDPOINT,
        json={
            "query": query,
            "query_vector": QUERY_VECTOR,
            "top_k": 5,
            "score_threshold": 0.0,
        },
    )


def ask_assistant(
    question: str,
):
    """
    Gửi request tới Assistant API.
    """

    return client.post(
        ASSISTANT_ENDPOINT,
        json={
            "question": question,
        },
    )


# =========================================================
# 1. USER OPENS APPLICATION
# =========================================================

def test_e2e_journey_application_available():
    """
    Bước 1:
    Người dùng mở Hành Chính AI.

    Application phải hoạt động.
    """

    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "Running"

    assert data["project"]

    assert data["version"]


# =========================================================
# 2. USER SEARCHES KNOWLEDGE
# =========================================================

def test_e2e_journey_user_searches_knowledge():
    """
    Bước 2:
    Người dùng tra cứu Knowledge Base.
    """

    response = search_knowledge()

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["query"] == KNOWLEDGE_QUERY

    assert data["results"]


# =========================================================
# 3. USER RECEIVES KNOWLEDGE RESULT
# =========================================================

def test_e2e_journey_knowledge_result():
    """
    Bước 3:
    Người dùng nhận được kết quả Knowledge.
    """

    response = search_knowledge()

    assert response.status_code == 200

    data = response.json()

    assert data["total"] >= 1

    assert len(
        data["results"]
    ) >= 1

    first_result = data["results"][0]

    assert first_result["vector_id"]

    assert first_result["content"]

    assert first_result["score"] is not None

    assert first_result["document_id"]


# =========================================================
# 4. USER ASKS ASSISTANT
# =========================================================

def test_e2e_journey_user_asks_assistant():
    """
    Bước 4:
    Người dùng chuyển sang Assistant
    và đặt câu hỏi.
    """

    response = ask_assistant(
        ASSISTANT_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["question"] == (
        ASSISTANT_QUESTION
    )


# =========================================================
# 5. ASSISTANT GENERATES ANSWER
# =========================================================

def test_e2e_journey_assistant_answer():
    """
    Bước 5:
    Assistant phải sinh câu trả lời.
    """

    response = ask_assistant(
        ASSISTANT_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert isinstance(
        data["answer"],
        str,
    )

    assert data["answer"].strip()


# =========================================================
# 6. ANSWER IS KNOWLEDGE BACKED
# =========================================================

def test_e2e_journey_answer_is_knowledge_backed():
    """
    Bước 6:
    Câu trả lời phải có nguồn Knowledge
    đi kèm.
    """

    response = ask_assistant(
        ASSISTANT_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"]

    assert data["citations"]

    assert (
        data["metadata"]["citation_count"]
        >= 1
    )


# =========================================================
# 7. USER CAN INSPECT SOURCE
# =========================================================

def test_e2e_journey_user_can_inspect_source():
    """
    Bước 7:
    Người dùng phải có thể nhận được
    thông tin nguồn của câu trả lời.
    """

    response = ask_assistant(
        ASSISTANT_QUESTION
    )

    assert response.status_code == 200

    citations = response.json()[
        "citations"
    ]

    assert citations

    citation = citations[0]

    assert citation["citation_id"]

    assert citation["source"]

    assert citation["document_id"]

    assert citation["page_number"] is not None

    assert citation["chunk_index"] is not None

    assert citation["content"]

    assert citation["label"]


# =========================================================
# 8. USER RECEIVES PIPELINE METADATA
# =========================================================

def test_e2e_journey_metadata():
    """
    Bước 8:
    Response phải có metadata phục vụ
    kiểm tra pipeline.
    """

    response = ask_assistant(
        ASSISTANT_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    metadata = data["metadata"]

    assert isinstance(
        metadata,
        dict,
    )

    assert metadata.get(
        "pipeline_stage"
    ) is not None

    assert metadata.get(
        "citation_count"
    ) is not None


# =========================================================
# 9. USER ASKS FOLLOW-UP QUESTION
# =========================================================

def test_e2e_journey_follow_up_question():
    """
    Bước 9:
    Người dùng tiếp tục hỏi một câu hỏi
    liên quan.
    """

    response = ask_assistant(
        FOLLOW_UP_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["question"] == (
        FOLLOW_UP_QUESTION
    )

    assert data["answer"]

    assert data["citations"]


# =========================================================
# 10. FOLLOW-UP HAS RELEVANT CONTENT
# =========================================================

def test_e2e_journey_follow_up_relevance():
    """
    Bước 10:
    Câu hỏi tiếp theo phải nhận được
    nội dung liên quan.
    """

    response = ask_assistant(
        FOLLOW_UP_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    answer = data["answer"].lower()

    assert (
        "chuyển đổi số"
        in answer
    )


# =========================================================
# 11. KNOWLEDGE AND ASSISTANT ARE CONSISTENT
# =========================================================

def test_e2e_journey_knowledge_assistant_consistency():
    """
    Bước 11:
    Knowledge và Assistant phải cùng truy xuất
    được nội dung liên quan.
    """

    knowledge_response = (
        search_knowledge(
            KNOWLEDGE_QUERY
        )
    )

    assert (
        knowledge_response.status_code
        == 200
    )

    knowledge_data = (
        knowledge_response.json()
    )

    assert knowledge_data[
        "results"
    ]

    assistant_response = (
        ask_assistant(
            ASSISTANT_QUESTION
        )
    )

    assert (
        assistant_response.status_code
        == 200
    )

    assistant_data = (
        assistant_response.json()
    )

    assert assistant_data[
        "citations"
    ]

    knowledge_document_ids = {
        item["document_id"]
        for item in knowledge_data[
            "results"
        ]
        if item["document_id"]
    }

    assistant_document_ids = {
        item["document_id"]
        for item in assistant_data[
            "citations"
        ]
        if item["document_id"]
    }

    assert (
        knowledge_document_ids
        & assistant_document_ids
    )


# =========================================================
# 12. USER JOURNEY RETAINS SOURCE CONTENT
# =========================================================

def test_e2e_journey_source_content_is_preserved():
    """
    Nội dung nguồn phải được giữ xuyên suốt
    từ Knowledge tới Assistant Citation.
    """

    knowledge_response = (
        search_knowledge()
    )

    assert (
        knowledge_response.status_code
        == 200
    )

    knowledge_results = (
        knowledge_response.json()[
            "results"
        ]
    )

    assert knowledge_results

    assistant_response = (
        ask_assistant(
            ASSISTANT_QUESTION
        )
    )

    assert (
        assistant_response.status_code
        == 200
    )

    citations = (
        assistant_response.json()[
            "citations"
        ]
    )

    assert citations

    knowledge_contents = {
        item["content"]
        for item in knowledge_results
    }

    citation_contents = {
        item["content"]
        for item in citations
    }

    assert (
        knowledge_contents
        & citation_contents
    )


# =========================================================
# 13. USER JOURNEY CAN REPEAT SEARCH
# =========================================================

def test_e2e_journey_repeat_knowledge_search():
    """
    Người dùng có thể tra cứu Knowledge
    nhiều lần trong cùng runtime.
    """

    queries = [
        "Chuyển đổi số",
        "Triển khai chuyển đổi số",
        "cải cách hành chính",
    ]

    for query in queries:
        response = search_knowledge(
            query
        )

        assert response.status_code == 200

        data = response.json()

        assert data["success"] is True

        assert data["query"] == query


# =========================================================
# 14. USER JOURNEY CAN REPEAT_ASSISTANT
# =========================================================

def test_e2e_journey_repeat_assistant():
    """
    Người dùng có thể hỏi Assistant
    nhiều lần liên tiếp.
    """

    questions = [
        ASSISTANT_QUESTION,
        FOLLOW_UP_QUESTION,
        ASSISTANT_QUESTION,
    ]

    for question in questions:
        response = ask_assistant(
            question
        )

        assert response.status_code == 200

        data = response.json()

        assert data["success"] is True

        assert data["question"] == question

        assert data["answer"]

        assert data["citations"]


# =========================================================
# 15. USER JOURNEY SURVIVES INVALID ACTION
# =========================================================

def test_e2e_journey_survives_invalid_action():
    """
    Một thao tác lỗi của người dùng không được
    làm hỏng hành trình tiếp theo.
    """

    invalid_response = ask_assistant(
        "   "
    )

    assert invalid_response.status_code in (
        400,
        422,
    )

    valid_response = ask_assistant(
        ASSISTANT_QUESTION
    )

    assert valid_response.status_code == 200

    data = valid_response.json()

    assert data["success"] is True

    assert data["answer"]

    assert data["citations"]


# =========================================================
# 16. USER JOURNEY RESPONSE CONTRACT
# =========================================================

def test_e2e_journey_response_contract():
    """
    Response cuối của User Journey phải
    đáp ứng đầy đủ contract.
    """

    response = ask_assistant(
        ASSISTANT_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    required_fields = {
        "success",
        "question",
        "answer",
        "citations",
        "metadata",
        "message",
    }

    assert required_fields.issubset(
        data.keys()
    )

    assert isinstance(
        data["success"],
        bool,
    )

    assert isinstance(
        data["question"],
        str,
    )

    assert isinstance(
        data["answer"],
        str,
    )

    assert isinstance(
        data["citations"],
        list,
    )

    assert isinstance(
        data["metadata"],
        dict,
    )


# =========================================================
# 17. USER JOURNEY CITATION COUNT
# =========================================================

def test_e2e_journey_citation_count():
    """
    citation_count phải khớp với citations
    mà người dùng nhận được.
    """

    response = ask_assistant(
        ASSISTANT_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["metadata"]["citation_count"]
        == len(data["citations"])
    )


# =========================================================
# 18. USER JOURNEY FINAL STATE
# =========================================================

def test_e2e_journey_final_state():
    """
    Sau toàn bộ các thao tác,
    hệ thống vẫn phải ở trạng thái hoạt động.
    """

    response = ask_assistant(
        FOLLOW_UP_QUESTION
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True

    assert data["answer"]

    assert data["citations"]

    assert data["metadata"]


# =========================================================
# 19. COMPLETE USER JOURNEY
# =========================================================

def test_e2e_complete_user_journey():
    """
    Complete User Journey:

        1. Open application
        2. Search Knowledge
        3. Read Knowledge result
        4. Ask Assistant
        5. Receive answer
        6. Inspect citation
        7. Ask follow-up
        8. Receive follow-up answer
    """

    # -----------------------------------------------------
    # STEP 1 - OPEN APPLICATION
    # -----------------------------------------------------

    root_response = client.get("/")

    assert root_response.status_code == 200

    root_data = root_response.json()

    assert root_data["status"] == "Running"

    # -----------------------------------------------------
    # STEP 2 - SEARCH KNOWLEDGE
    # -----------------------------------------------------

    knowledge_response = search_knowledge()

    assert (
        knowledge_response.status_code
        == 200
    )

    knowledge_data = (
        knowledge_response.json()
    )

    assert knowledge_data["success"]

    assert knowledge_data["results"]

    # -----------------------------------------------------
    # STEP 3 - READ KNOWLEDGE
    # -----------------------------------------------------

    knowledge_result = (
        knowledge_data["results"][0]
    )

    assert knowledge_result["content"]

    assert knowledge_result["document_id"]

    # -----------------------------------------------------
    # STEP 4 - ASK ASSISTANT
    # -----------------------------------------------------

    assistant_response = (
        ask_assistant(
            ASSISTANT_QUESTION
        )
    )

    assert (
        assistant_response.status_code
        == 200
    )

    assistant_data = (
        assistant_response.json()
    )

    assert assistant_data["success"]

    # -----------------------------------------------------
    # STEP 5 - RECEIVE ANSWER
    # -----------------------------------------------------

    assert assistant_data["answer"]

    # -----------------------------------------------------
    # STEP 6 - INSPECT CITATION
    # -----------------------------------------------------

    citations = assistant_data[
        "citations"
    ]

    assert citations

    citation = citations[0]

    assert citation["citation_id"]

    assert citation["source"]

    assert citation["document_id"]

    assert citation["content"]

    # -----------------------------------------------------
    # STEP 7 - FOLLOW-UP
    # -----------------------------------------------------

    follow_up_response = (
        ask_assistant(
            FOLLOW_UP_QUESTION
        )
    )

    assert (
        follow_up_response.status_code
        == 200
    )

    follow_up_data = (
        follow_up_response.json()
    )

    # -----------------------------------------------------
    # STEP 8 - FINAL ANSWER
    # -----------------------------------------------------

    assert follow_up_data[
        "success"
    ] is True

    assert follow_up_data[
        "answer"
    ]

    assert follow_up_data[
        "citations"
    ]

    assert (
        follow_up_data[
            "metadata"
        ][
            "citation_count"
        ]
        == len(
            follow_up_data[
                "citations"
            ]
        )
    )


# =========================================================
# 20. COMPLETE USER JOURNEY GATE
# =========================================================

def test_e2e_complete_user_journey_gate():
    """
    FINAL GATE của Task 12.16.6.

    Xác nhận:

        Application
             ↓
        Knowledge
             ↓
        Retrieval
             ↓
        Assistant
             ↓
        RAG
             ↓
        Answer
             ↓
        Citation
             ↓
        Follow-up
             ↓
        Stable Runtime
    """

    # Application
    root_response = client.get("/")

    assert root_response.status_code == 200

    # Knowledge
    knowledge_response = search_knowledge()

    assert (
        knowledge_response.status_code
        == 200
    )

    knowledge_data = (
        knowledge_response.json()
    )

    assert knowledge_data["success"]

    assert knowledge_data["results"]

    # Assistant
    assistant_response = (
        ask_assistant(
            ASSISTANT_QUESTION
        )
    )

    assert (
        assistant_response.status_code
        == 200
    )

    assistant_data = (
        assistant_response.json()
    )

    assert assistant_data["success"]

    assert assistant_data["answer"]

    assert assistant_data["citations"]

    # Citation
    citation = (
        assistant_data[
            "citations"
        ][0]
    )

    assert citation["citation_id"]

    assert citation["source"]

    assert citation["document_id"]

    assert citation["page_number"] is not None

    assert citation["chunk_index"] is not None

    assert citation["content"]

    assert citation["label"]

    # Follow-up
    follow_up_response = (
        ask_assistant(
            FOLLOW_UP_QUESTION
        )
    )

    assert (
        follow_up_response.status_code
        == 200
    )

    follow_up_data = (
        follow_up_response.json()
    )

    assert follow_up_data[
        "success"
    ] is True

    assert follow_up_data[
        "answer"
    ]

    assert follow_up_data[
        "citations"
    ]

    # Metadata
    assert (
        follow_up_data[
            "metadata"
        ][
            "citation_count"
        ]
        == len(
            follow_up_data[
                "citations"
            ]
        )
    )