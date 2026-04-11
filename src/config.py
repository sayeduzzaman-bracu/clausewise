from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "input"

SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}

GEMINI_MODEL = "gemini-2.5-flash"