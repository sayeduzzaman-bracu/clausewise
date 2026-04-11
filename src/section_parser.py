import re
from typing import List, Dict


SECTION_PATTERN = re.compile(
    r"(§\s*\d+\s+[^\n]+)([\s\S]*?)(?=(?:\n§\s*\d+\s+[^\n]+)|\Z)",
    re.MULTILINE
)


def parse_sections(doc_name: str, text: str) -> List[Dict]:
    """
    Parse document text into structured legal-style sections.

    Example section header:
    §13 Payment Terms
    """
    sections = []

    matches = SECTION_PATTERN.findall(text)

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