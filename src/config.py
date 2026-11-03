# ===== Config =====
import os

from dotenv import load_dotenv

load_dotenv()

# === load value from env ===
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")  # Optional; defaults to the official OpenAI endpoint.
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Optional; uses a default model.
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS"))