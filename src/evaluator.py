from typing import List, Dict

from google import genai


def build_evaluation_context(query: str, answer: str, sections: List[Dict]) -> str:
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
Question:
{query}

Answer to evaluate:
{answer}

Source text:
{joined_context}
""".strip()


def build_evaluation_prompt(evaluation_context: str, language: str = "sv") -> str:
    if language == "en":
        return f"""
You are a strict quality reviewer for a document QA system.

Evaluate the answer ONLY based on the source text.
Check especially:
1. Whether the answer is grounded in the source text
2. Whether the answer contains hallucinated information
3. Whether the answer includes source references
4. Whether the answer is sufficiently complete for the question

Always answer in English.

Use EXACTLY this format:

Score: <an integer between 1 and 10>
Grounded: <Yes or No>
Sources present: <Yes or No>
Problems:
- <short point 1>
- <short point 2>
- <short point 3>

Rules:
- If no major problems exist, still include at least one bullet under "Problems:" such as "- No major problems detected."
- Be short and clear.
- Do not invent anything unsupported by the source text.

{evaluation_context}
""".strip()

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
    language: str = "sv",
) -> str:
    client = genai.Client(api_key=api_key)

    evaluation_context = build_evaluation_context(query, answer, sections)
    prompt = build_evaluation_prompt(evaluation_context, language=language)

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    if response.text:
        return response.text.strip()

    return "Evaluation could not be generated." if language == "en" else "Utvärdering kunde inte genereras."
