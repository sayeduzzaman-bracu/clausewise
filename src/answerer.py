from typing import List, Dict

from google import genai


def build_context(sections: List[Dict]) -> str:
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


def build_prompt(query: str, context: str, language: str = "sv") -> str:
    if language == "en":
        return f"""
You are a careful document assistant.

Answer only based on the source text below.
Do not make anything up.
If the answer is not clearly found in the source text, clearly say that the information was not found in the uploaded documents.

Always answer in English.

Use this format:

Answer:
<your answer in English>

Sources:
- <document name>, <section>
- <document name>, <section>

Source text:
{context}

Question:
{query}
""".strip()

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
    language: str = "sv",
) -> str:
    client = genai.Client(api_key=api_key)

    context = build_context(sections)
    prompt = build_prompt(query, context, language=language)

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    if response.text:
        return response.text.strip()

    return "No answer could be generated." if language == "en" else "Inget svar kunde genereras."
