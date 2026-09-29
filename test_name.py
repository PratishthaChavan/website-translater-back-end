from services.gema_service_vision import analyze_image


def main():

    with open(
        "images/deimon10.png",
        "rb"
    ) as file:
        image_bytes = file.read()
    prompt = """
Look carefully at the Japanese name in this manga image.

There is a large kanji name with small furigana above it.

Identify:

1. The large kanji characters of the person's name.
2. The furigana attached to those kanji.
3. The reading of the person's name according to the furigana.

Important:
- Read only what is visually present.
- Do not guess from dictionary knowledge.
- Do not translate.
- Do not romanize the name.
- Treat さん as an honorific, NOT as part of the person's name.
- The furigana determines how the kanji name is read.

Return ONLY:

KANJI: <large kanji name>
FURIGANA: <furigana>
READING: <same reading in hiragana>

Do not add explanations.
"""

    result = analyze_image(
        image_bytes,
        prompt
    )

    print("\n========== GEMMA ==========\n")
    print(result)
    print("\n===========================\n")


if __name__ == "__main__":
    main()