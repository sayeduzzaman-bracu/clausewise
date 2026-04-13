from pathlib import Path
import tempfile

from extractor import extract_all, extract_txt
from section_parser import parse_sections
from retriever import retrieve_sections


def load_all_sections_from_folder(input_dir):
    docs = extract_all(input_dir)

    all_sections = []
    for doc in docs:
        sections = parse_sections(doc["name"], doc["text"])
        all_sections.extend(sections)

    return all_sections


def load_all_sections_from_uploads(uploaded_files):
    all_sections = []

    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        suffix = Path(file_name).suffix.lower()

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = Path(tmp.name)

        if suffix == ".txt":
            text = extract_txt(tmp_path)
            sections = parse_sections(file_name, text)
            all_sections.extend(sections)

    return all_sections


def run_retrieval(query, all_sections, top_k=3):
    return retrieve_sections(query, all_sections, top_k=top_k)
    return retrieve_sections(query, all_sections, top_k=top_k)
