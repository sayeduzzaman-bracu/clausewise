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
    """
    Load uploaded files safely and return:
    - all_sections: parsed sections
    - file_reports: per-file processing results
    """
    all_sections = []
    file_reports = []

    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        suffix = Path(file_name).suffix.lower()

        if suffix != ".txt":
            file_reports.append(
                {
                    "file_name": file_name,
                    "status": "unsupported",
                    "message": "Unsupported file type. Only .txt is supported right now.",
                    "sections_found": 0,
                }
            )
            continue

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = Path(tmp.name)

            text = extract_txt(tmp_path)

            if not text.strip():
                file_reports.append(
                    {
                        "file_name": file_name,
                        "status": "empty",
                        "message": "The file appears empty or unreadable.",
                        "sections_found": 0,
                    }
                )
                continue

            sections = parse_sections(file_name, text)
            all_sections.extend(sections)

            parser_mode = "legal_sections" if any(sec["section_id"].startswith("§") for sec in sections) else "fallback_parts"

            file_reports.append(
                {
                    "file_name": file_name,
                    "status": "processed",
                    "message": f"Processed successfully using {parser_mode}.",
                    "sections_found": len(sections),
                }
            )

        except Exception as e:
            file_reports.append(
                {
                    "file_name": file_name,
                    "status": "error",
                    "message": f"Processing failed: {str(e)}",
                    "sections_found": 0,
                }
            )

    return all_sections, file_reports


def run_retrieval(query, all_sections, top_k=3):
    return retrieve_sections(query, all_sections, top_k=top_k)
