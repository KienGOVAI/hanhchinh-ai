from app.ocr.ai import OCRAIService
from app.ocr.models import OCRDocument
from app.knowledge.assistant import AssistantResponse


class FakeAssistantService:
    def answer(self, question: str) -> AssistantResponse:
        return AssistantResponse(
            answer="Đây là kết quả AI giả lập từ nội dung OCR.",
            query=question,
            citations=[],
            metadata={
                "provider": "fake",
            },
        )


document = OCRDocument(
    text="CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM"
)

service = OCRAIService(
    assistant_service=FakeAssistantService()
)

result = service.process(
    document=document,
    instruction="Hãy tóm tắt nội dung văn bản.",
)

print("OCR AI SERVICE TEST OK")
print("Answer:", result.answer)
print("OCR text:", result.ocr_text)
print("Instruction:", result.instruction)
print("Metadata:", result.metadata)
