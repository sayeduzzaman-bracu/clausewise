from typing import List, Dict

from google import genai


def build_context(sections: List[Dict]) -> str:
    """Build a grounded context block from retrieved sections."""
    context_parts = []

    for i, section in enumerate(sections, start=1):
        context_parts.append(
            f"""[Source {i}]
Document: {section["doc_name"]}
Section: {section["full_section_title"]}
Text: {section["text"]}
"""
        )

    return "\n".join(context_parts).strip()


def build_prompt(query: str, context: str) -> str:
    """Create a strict grounded-answer prompt in Swedish."""
    return f"""
Du är en noggrann dokumentassistent.

Svara endast baserat på källtexten nedan.
Hitta inte på något.
Om svaret inte tydligt finns i källtexten, säg tydligt på svenska att informationen inte hittades i de uppladdade dokumenten.

Svara alltid på svenska.

Använd detta format:

Svar:
<ditt svar på svenska>

Källor:
- <dokumentnamn>, <sektion>
- <dokumentnamn>, <sektion>

Källtext:
{context}

Fråga:
{query}
""".strip()


def generate_answer(
    query: str,
    sections: List[Dict],
    api_key: str,
    model_name: str,
) -> str:
    """Generate a grounded answer from retrieved sections using Gemini."""
    client = genai.Client(api_key=api_key)

    context = build_context(sections)
    prompt = build_prompt(query, context)

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    return response.text.strip() if response.text else "Inget svar kunde genereras."