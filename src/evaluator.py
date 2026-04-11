from typing import List, Dict

from google import genai


def build_evaluation_context(query: str, answer: str, sections: List[Dict]) -> str:
    """Build the context block used for answer evaluation."""
    context_parts = []

    for i, section in enumerate(sections, start=1):
        context_parts.append(
            f"""[Source {i}]
Document: {section["doc_name"]}
Section: {section["full_section_title"]}
Text: {section["text"]}
"""
        )

    joined_context = "\n".join(context_parts).strip()

    return f"""
Fråga:
{query}

Svar att utvärdera:
{answer}

Källtext:
{joined_context}
""".strip()


def build_evaluation_prompt(evaluation_context: str) -> str:
    """Create a strict evaluation prompt in Swedish."""
    return f"""
Du är en strikt kvalitetsgranskare för ett dokument-QA-system.

Utvärdera svaret ENDAST baserat på källtexten.
Kontrollera särskilt:
1. Om svaret är grundat i källtexten
2. Om svaret innehåller påhittad information
3. Om svaret innehåller källhänvisningar
4. Om svaret är tillräckligt komplett för frågan

Svara alltid på svenska.

Använd EXAKT detta format:

Poäng: <ett heltal mellan 1 och 10>
Grundat: <Ja eller Nej>
Källor finns: <Ja eller Nej>
Problem:
- <kort punkt 1>
- <kort punkt 2>
- <kort punkt 3>

Regler:
- Om inget problem finns, skriv ändå minst en punkt under "Problem:" och skriv t.ex. "- Inga större problem upptäcktes."
- Var kort och tydlig.
- Hitta inte på något som inte stöds av källtexten.

{evaluation_context}
""".strip()


def evaluate_answer(
    query: str,
    answer: str,
    sections: List[Dict],
    api_key: str,
    model_name: str,
) -> str:
    """Evaluate a generated answer against retrieved source sections."""
    client = genai.Client(api_key=api_key)

    evaluation_context = build_evaluation_context(query, answer, sections)
    prompt = build_evaluation_prompt(evaluation_context)

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    return response.text.strip() if response.text else "Utvärdering kunde inte genereras."