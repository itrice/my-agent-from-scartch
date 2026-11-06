# ===== Config =====
import os

from dotenv import load_dotenv

# === File
MAX_FILE_ENTRIES = 200
MAX_GREP_ENTRIES = 100
MAX_FILE_READ_LIMIT = 2000

# === Shell    
SHELL_MAX_TIMEOUT = 30
SHELL_MAX_OUTPUT = 2000

load_dotenv()

# === load value from env ===
API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("OPENAI_BASE_URL")  # Optional; defaults to the official OpenAI endpoint.
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # Optional; uses a default model.
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS"))
