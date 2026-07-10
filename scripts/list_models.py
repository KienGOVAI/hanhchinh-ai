import sys
from pathlib import Path

# Thêm thư mục gốc của project vào PYTHONPATH
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from google import genai
from app.core.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

print("=" * 60)
print("DANH SÁCH MODEL KHẢ DỤNG")
print("=" * 60)

for model in client.models.list():
    print(model.name)