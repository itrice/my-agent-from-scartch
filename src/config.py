# ===== Config =====
import os

from dotenv import load_dotenv

load_dotenv()

# === load value from env ===
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")  # 可选，不设置则用 OpenAI 官方
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # 可选，给个默认值
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS"))