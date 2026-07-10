import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from app.providers.openrouter_provider import OpenRouterProvider

provider = OpenRouterProvider()

result = provider.generate(
    "Hãy trả lời đúng duy nhất một từ: XinChao"
)

print(result)