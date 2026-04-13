from pathlib import Path
from utils import normalize_text


def extract_txt(file_path: Path):
    text = file_path.read_text(encoding="utf-8", errors="ignore")
    return normalize_text(text)


def extract_all(input_dir: Path):
    docs = []

    for file in input_dir.iterdir():
        if file.suffix.lower() == ".txt":
            text = extract_txt(file)
            docs.append({
                "name": file.name,
                "text": text
            })

    return docs
