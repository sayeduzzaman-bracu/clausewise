import re
from collections import defaultdict


def extract_numbers(text):
    """Extract numeric values from text."""
    return re.findall(r"\d+", text)


def find_contradictions(sections):
    """
    Detect possible contradictions between sections
    with the same section_id across different documents.
    """
    grouped = defaultdict(list)

    for sec in sections:
        grouped[sec["section_id"]].append(sec)

    contradictions = []

    for section_id, group in grouped.items():
        if len(group) < 2:
            continue

        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                sec1 = group[i]
                sec2 = group[j]

                nums1 = extract_numbers(sec1["text"])
                nums2 = extract_numbers(sec2["text"])

                if nums1 != nums2:
                    contradictions.append({
                        "section_id": section_id,
                        "doc1": sec1["doc_name"],
                        "doc2": sec2["doc_name"],
                        "text1": sec1["text"],
                        "text2": sec2["text"],
                        "numbers1": nums1,
                        "numbers2": nums2,
                    })

    return contradictions