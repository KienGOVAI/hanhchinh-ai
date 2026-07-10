from google import genai

from app.core.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
)


class OpenAIProvider:

    def __init__(self):

        if not GEMINI_API_KEY:
            raise ValueError(
                "Thiếu GEMINI_API_KEY trong file .env"
            )

        self.client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    def generate(
        self,
        prompt: str
    ) -> str:

        try:

            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )

            print("=" * 80)
            print(response)
            print("=" * 80)

            if hasattr(response, "text") and response.text:
                return response.text

            return str(response)

        except Exception as ex:

            import traceback

            traceback.print_exc()

            return f"Lỗi Gemini:\n\n{ex}"