import torch
import time
import requests
import os
# OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/v1/chat/completions"
)
MODEL_NAME = "gemma3:12b"
KNOWN_NAMES = """
KNOWN CHARACTER NAMES / READINGS:
- 和さん → Nagumo-san
- いつか → Itsuka

IMPORTANT:
- These are confirmed character names.
- When these Japanese names appear, use the confirmed English name.
- Do NOT reinterpret the kanji using its dictionary reading.
- Do NOT change Nagumo to Nagomi.
"""
def translate_with_llama(prompt):

    response = requests.post(
        OLLAMA_URL,
        
        json={
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0,
            "max_tokens": 384
        },
        timeout=300
    )

    response.raise_for_status()

    data = response.json()

    return data["choices"][0]["message"]["content"].strip()
t = time.perf_counter()


LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "fr": "French",
    "es": "Spanish",
    "de": "German",
    "pt": "Portuguese",
    "zh": "Chinese",
    "ko": "Korean",
    "ar": "Arabic"
}
def text_translator(texts, trg):

    if not texts:
        return []

    target_language = LANGUAGES.get(
        trg,
        trg
    )

    page_context = "\n".join(
    (
            f"{i + 1}. {item['text']} "
            f"(reading: {item['reading']})"
            if item.get("is_name")
            else f"{i + 1}. {item['text']}"
        )
        for i, item in enumerate(texts)
    )
    prompt = (
    "You are a professional Japanese manga translator.\n\n"

    f"Translate all dialogue into natural {target_language}.\n\n"

    "Use the entire page dialogue as context to understand "
    "omitted subjects, relationships, pronouns, tone, emotion, "
    "dialect, and proper names.\n\n"

    + KNOWN_NAMES + "\n\n"

    "Rules:\n"
    "- Preserve character names.\n"
    "- Use confirmed character name readings when provided above.\n"
    "- Never translate a character name by its dictionary meaning.\n"
    "- Never invent or replace names.\n"
    "- Keep character names consistent.\n"
    "- Do not summarize.\n"
    "- Do not omit information.\n"
    "- Preserve emotion and speaker intent.\n"
    "- Preserve dialect naturally.\n"
    "- Return exactly one translation for each numbered dialogue.\n"
    "- Keep the original numbering.\n"
    "- Return only the translations.\n\n"

    f"Translate exactly {len(texts)} dialogue items.\n\n"

    "PAGE DIALOGUE:\n"
    f"{page_context}\n\n"

    "TRANSLATIONS:"
)

    output_text = translate_with_llama(
        prompt
    )
    print("\n========== RAW GEMMA OUTPUT ==========")
    print(output_text)
    print("======================================\n")

    print("EXPECTED BLOCKS:", len(texts))

    translated_lines = [
        line.strip()
        for line in output_text.splitlines()
        if line.strip()
    ]

    results = []

    for i, item in enumerate(texts):

        translation = ""

        if i < len(translated_lines):

            translation = translated_lines[i]

            prefix = f"{i + 1}."

            if translation.startswith(prefix):
                translation = translation[
                    len(prefix):
                ].strip()

        results.append({
            "text": item["text"],
            "translation": translation,
            "box": item["box"]
        })

    return results