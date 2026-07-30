from app.services.ai_service import AIService


ai = AIService()

result = ai.generate_document(
    document_type="cong_van",
    title="Tăng cường chuyển đổi số",
    content="Soạn công văn về tăng cường chuyển đổi số tại UBND xã."
)

print(result)