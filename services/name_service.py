import re
import cv2

from services.gema_service_vision import analyze_image


# Japanese honorifics / name suffixes.
# These are only used to decide whether the OCR result
# should be checked by Gemma Vision.
NAME_SUFFIXES = (
    "さん",
    "ちゃん",
    "くん",
    "君",
    "様",
    "さま",
    "先生",
)


def is_name_candidate(text):
    """
    Check whether MangaOCR's result looks like
    a Japanese name followed by an honorific.

    Examples:

        和さん       -> True
        太郎くん     -> True
        田中先生     -> True

        ちょっと待って -> False
        帰んの        -> False
    """

    if not text:
        return False

    text = text.strip()

    if not text:
        return False

    return text.endswith(NAME_SUFFIXES)


def image_to_bytes(image):
    """
    Convert an OpenCV BGR image into PNG bytes.
    """

    success, encoded = cv2.imencode(
        ".png",
        image
    )

    if not success:
        return None

    return encoded.tobytes()


def build_name_prompt(text):
    return f"""
You are reading a Japanese manga character name.

A text detector found a possible name region in the image.
MangaOCR detected:

{text}

The image you are seeing is the detected name region.

Your job is to inspect the IMAGE itself.

The region may contain:
- large kanji characters
- small furigana beside or above the kanji
- an honorific such as さん

IMPORTANT:

- Read the small furigana directly from the image.
- The furigana visible in the image is the source of the name reading.
- Do NOT infer the reading from the kanji.
- Do NOT use dictionary knowledge to determine the reading.
- Do NOT guess the reading.
- Do NOT replace the visible furigana with a common Japanese name reading.
- Do NOT use the MangaOCR result as the name reading.
- MangaOCR is only provided as a hint about which region contains a possible name.
- Inspect the actual small characters in the image.
- さん, ちゃん, くん, 君, 様, さま, and 先生 are honorifics.
- Do not include an honorific as part of the person's name.

First identify the large kanji characters that form the name.

Then identify the small furigana characters visually.

Then return the furigana exactly as it appears in the image.

Return ONLY:

KANJI: <large kanji name>
FURIGANA: <small furigana read from image>
READING: <same furigana reading>

Do not add explanations.
Do not translate.
Do not romanize.
"""


def parse_name_result(result):
    """
    Parse Gemma's response.

    Expected:

        KANJI: 和
        FURIGANA: なごむ
        READING: なごむ
    """

    if not result:
        return None

    kanji_match = re.search(
        r"^\s*KANJI:\s*(.+?)\s*$",
        result,
        re.MULTILINE
    )

    furigana_match = re.search(
        r"^\s*FURIGANA:\s*(.+?)\s*$",
        result,
        re.MULTILINE
    )

    reading_match = re.search(
        r"^\s*READING:\s*(.+?)\s*$",
        result,
        re.MULTILINE
    )

    if not kanji_match:
        return None

    if not reading_match:
        return None

    kanji = kanji_match.group(1).strip()

    furigana = ""

    if furigana_match:
        furigana = furigana_match.group(1).strip()

    reading = reading_match.group(1).strip()

    if not kanji:
        return None

    if not reading:
        return None

    return {
        "kanji": kanji,
        "furigana": furigana,
        "reading": reading
    }


def resolve_name_with_gemma(
    image,
    text,
    box=None
):
    print(
        f"\n[NameResolver] MangaOCR: {text}"
    )

    if box is None:
        print("[NameResolver] No box provided.")
        return None

    x1, y1, x2, y2 = map(int, box)

    height, width = image.shape[:2]

    x1 = max(0, min(x1, width - 1))
    y1 = max(0, min(y1, height - 1))
    x2 = max(0, min(x2, width))
    y2 = max(0, min(y2, height))

    crop = image[
        y1:y2,
        x1:x2
    ]

    if crop.size == 0:
        print("[NameResolver] EMPTY CROP")
        return None

    print(
        "[NameResolver] Crop shape:",
        crop.shape
    )
    crop = cv2.resize(
        crop,
        None,
        fx=4,
        fy=4,
        interpolation=cv2.INTER_CUBIC
    )

    print(
        "[NameResolver] Upscaled crop:",
        crop.shape
    )

    cv2.imwrite(
        "debug_name_crop.png",
        crop
    )

    print(
        "[NameResolver] Saved debug_name_crop.png"
    )

    # ------------------------------------------
    # Convert crop to bytes
    # ------------------------------------------

    image_bytes = image_to_bytes(
        crop
    )

    if image_bytes is None:
        print(
            "[NameResolver] Could not encode crop."
        )
        return None
    prompt = build_name_prompt(text)

    print(
        "[NameResolver] Sending CROP to Gemma..."
    )

    try:

        result = analyze_image(
            image_bytes,
            prompt
        )

    except Exception as e:

        print(
            f"[NameResolver] Gemma failed: {e}"
        )

        return None

    print(
        "\n========== GEMMA NAME =========="
    )

    print(result)

    print(
        "================================\n"
    )

    parsed = parse_name_result(result)

    if parsed is None:

        print(
            "[NameResolver] Could not parse Gemma result."
        )

        return None

    print(
        "[NameResolver] Resolved:"
    )

    print(
        f"KANJI: {parsed['kanji']}"
    )

    print(
        f"FURIGANA: {parsed['furigana']}"
    )

    print(
        f"READING: {parsed['reading']}"
    )

    return parsed
def resolve_name(
    image,
    text,
    box=None
):
    """
    Main function used by OCR service.

    MangaOCR is the fast first step.

    Gemma Vision is only called when the OCR
    result looks like a name with an honorific.
    """

    print(
        f"\n[NameResolver] Checking: {repr(text)}"
    )

    if not is_name_candidate(text):

        print(
            "[NameResolver] Not a name candidate."
        )

        return None

    print(
        f"[NameResolver] Possible name: {text}"
    )
    print(resolve_name_with_gemma(
        image,  
        text,
        box
    ))
    return resolve_name_with_gemma(
        image,  
        text,
        box
    )