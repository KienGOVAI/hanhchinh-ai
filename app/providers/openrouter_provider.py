import requests

from app.core.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
)


class OpenRouterProvider:

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def generate(
        self,
        prompt: str
    ) -> str:

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Hanh Chinh AI"
        }

        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        try:

            response = requests.post(
                self.BASE_URL,
                headers=headers,
                json=payload,
                timeout=120
            )

            print("=" * 80)
            print(response.status_code)
            print(response.text)
            print("=" * 80)

            response.raise_for_status()

            data = response.json()

            return data["choices"][0]["message"]["content"]

        except Exception as ex:

            return f"Lỗi OpenRouter:\n\n{ex}"