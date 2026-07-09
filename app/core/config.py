from dotenv import load_dotenv
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")

APP_NAME = os.getenv("APP_NAME", "Hành Chính AI")

APP_VERSION = os.getenv("APP_VERSION", "0.0.1")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

DATABASE_URL = os.getenv("DATABASE_URL", "")

DEBUG = os.getenv("DEBUG", "True")