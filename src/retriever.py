import re
from typing import List, Dict


def tokenize(text: str) -> List[str]:
    """Simple lowercase word tokenizer."""
    return re.findall(r"\w+", text.lower())


def extract_section_reference(query: str) -> str | None:
    """Find references like §13 in the query."""
    match = re.search(r"§\s*(\d+)", query)
    if match:
        return f"§{match.group(1)}"
    return None


def score_section(query: str, section: Dict) -> int:
    """
    Score a section against the user query.
    Higher score = more relevant.
    """
    score = 0
    query_lower = query.lower()

    query_tokens = set(tokenize(query))
    title_tokens = set(tokenize(section["section_title"]))
    body_tokens = set(tokenize(section["text"]))
    full_header_tokens = set(tokenize(section["full_section_title"]))

    # Strong boost for exact section reference like §13
    requested_section = extract_section_reference(query)
    if requested_section and requested_section == section["section_id"]:
        score += 100

    # Title/header token overlap
    score += len(query_tokens & title_tokens) * 10
    score += len(query_tokens & full_header_tokens) * 8

    # Body token overlap
    score += len(query_tokens & body_tokens) * 3

    # Small bonus if exact section title text appears in query
    if section["section_title"].lower() in query_lower:
        score += 20

    return score


def retrieve_sections(query: str, sections: List[Dict], top_k: int = 3) -> List[Dict]:
    """Return top matching sections."""
    scored = []

    for section in sections:
        score = score_section(query, section)
        item = section.copy()
        item["score"] = score
        scored.append(item)

    scored.sort(key=lambda x: x["score"], reverse=True)

    # Keep only positive-score results
    return [item for item in scored if item["score"] > 0][:top_k]