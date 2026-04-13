import re
from typing import List, Dict


SECTION_PATTERN = re.compile(
    r"(§\s*\d+\s+[^\n]+)([\s\S]*?)(?=(?:\n§\s*\d+\s+[^\n]+)|\Z)",
    re.MULTILINE
)


def parse_sections(doc_name: str, text: str) -> List[Dict]:
    """
    Parse document text into structured sections.

    Primary mode:
    - Legal-style sections like: §13 Payment Terms

    Fallback mode:
    - If no §-style sections are found, split by paragraph blocks
      into pseudo-sections so the app still works instead of failing.
    """
    sections = []

    matches = SECTION_PATTERN.findall(text)

    if matches:
        for match in matches:
            raw_header = match[0].strip()
            raw_body = match[1].strip()

            section_id_match = re.match(r"(§\s*\d+)", raw_header)
            section_id = section_id_match.group(1).replace(" ", "") if section_id_match else "UNKNOWN"
            section_title = raw_header[len(section_id_match.group(1)):].strip() if section_id_match else raw_header

            sections.append(
                {
                    "doc_name": doc_name,
                    "section_id": section_id,
                    "section_title": section_title,
                    "full_section_title": raw_header,
                    "text": raw_body,
                }
            )
        return sections

    # Fallback: paragraph-based pseudo sections
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

    for i, paragraph in enumerate(paragraphs, start=1):
        preview = paragraph.split("\n", 1)[0][:60].strip()
        title = preview if preview else f"Part {i}"

        sections.append(
            {
                "doc_name": doc_name,
                "section_id": f"PART_{i}",
                "section_title": title,
                "full_section_title": f"Part {i}",
                "text": paragraph,
            }
        )

    return sections
