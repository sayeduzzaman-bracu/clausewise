from typing import List, Dict

from google import genai


def build_decision_context(sections: List[Dict], contradictions: List[Dict]) -> str:
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


def build_decision_prompt(context: str, language: str = "sv") -> str:
    if language == "en":
        return f"""
You are a careful document analyst.

Analyze the document content and any contradictions.
Your goal is to provide business- or decision-relevant insights.

Always answer in English.

Use EXACTLY this format:

Key Findings:
- <point 1>
- <point 2>
- <point 3>

Risks:
- <risk 1>
- <risk 2>
- <risk 3>

Recommendations:
- <recommendation 1>
- <recommendation 2>
- <recommendation 3>

Rules:
- Base your analysis only on the context.
- Do not make anything up.
- If contradictions exist, mention why they may matter.
- If an area lacks obvious risk, write a cautious and reasonable observation.

Context:
{context}
""".strip()

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
    language: str = "sv",
) -> str:
    client = genai.Client(api_key=api_key)

    context = build_decision_context(sections, contradictions)
    prompt = build_decision_prompt(context, language=language)

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    if response.text:
        return response.text.strip()

    return "No decision analysis could be generated." if language == "en" else "Ingen beslutsanalys kunde genereras."
