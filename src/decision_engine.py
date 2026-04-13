from typing import List, Dict

from google import genai


def build_decision_context(sections: List[Dict], contradictions: List[Dict]) -> str:
    """Build structured context for insight/risk/recommendation generation."""
    section_parts = []
    for i, sec in enumerate(sections, start=1):
        section_parts.append(
            f"""[Section {i}]
Document: {sec["doc_name"]}
Section: {sec["full_section_title"]}
Text: {sec["text"]}
"""
        )

    contradiction_parts = []
    if contradictions:
        for i, c in enumerate(contradictions, start=1):
            contradiction_parts.append(
                f"""[Contradiction {i}]
Section ID: {c["section_id"]}
Document 1: {c["doc1"]}
Text 1: {c["text1"]}
Document 2: {c["doc2"]}
Text 2: {c["text2"]}
Numbers: {c["numbers1"]} vs {c["numbers2"]}
"""
            )
    else:
        contradiction_parts.append("No contradictions detected.")

    return f"""
Parsed Sections:
{chr(10).join(section_parts)}

Detected Contradictions:
{chr(10).join(contradiction_parts)}
""".strip()


def build_decision_prompt(context: str) -> str:
    """Prompt for decision-oriented analysis."""
    return f"""
Du är en noggrann dokumentanalytiker.

Analysera dokumentinnehållet och eventuella motsägelser.
Ditt mål är att ge affärs- eller beslutsrelevanta insikter.

Svara alltid på svenska.

Använd EXAKT detta format:

Nyckelfynd:
- <punkt 1>
- <punkt 2>
- <punkt 3>

Risker:
- <risk 1>
- <risk 2>
- <risk 3>

Rekommendationer:
- <rekommendation 1>
- <rekommendation 2>
- <rekommendation 3>

Regler:
- Basera dig endast på informationen i kontexten.
- Hitta inte på något.
- Om det finns motsägelser, nämn varför de kan vara viktiga.
- Om något område saknar uppenbar risk, skriv en försiktig och rimlig observation.

Kontext:
{context}
""".strip()


def generate_decision_analysis(
    sections: List[Dict],
    contradictions: List[Dict],
    api_key: str,
    model_name: str,
) -> str:
    """Generate decision-oriented analysis from parsed sections and contradictions."""
    client = genai.Client(api_key=api_key)

    context = build_decision_context(sections, contradictions)
    prompt = build_decision_prompt(context)

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    return response.text.strip() if response.text else "Ingen beslutsanalys kunde genereras."
    prompt = build_decision_prompt(context)

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    return response.text.strip() if response.text else "Ingen beslutsanalys kunde genereras."
