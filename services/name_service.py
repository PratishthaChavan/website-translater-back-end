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
This is a crop of a Japanese manga speech bubble containing: {text}

Above or beside the kanji there are small kana (furigana) showing its reading.
Read ALL of the furigana characters, in order. It is usually 2-4 kana long.
Do not stop after the first character.
Do not guess the reading from the kanji. If there is no furigana, answer NONE.
Ignore the honorific (さん, ちゃん, くん, 君, 様, さま, 先生).

Return ONLY:
KANJI: <kanji of the name>
FURIGANA: <all furigana kana, or NONE>
READING: <same as FURIGANA, or NONE>
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

def is_valid_reading(reading):
    # pure hiragana, at least 2 characters (e.g. なごむ)
    return bool(re.fullmatch(r"[\u3041-\u3096ー]{2,}", reading))

def resolve_name_with_gemma(image, text, box=None):
    print(f"\n[NameResolver] MangaOCR: {text}")

    if box is None:
        print("[NameResolver] No box provided.")
        return None

    x1, y1, x2, y2 = map(int, box)
    height, width = image.shape[:2]
    bw, bh = x2 - x1, y2 - y1

    # Furigana sits above/right of the kanji, so pad those sides the most
    x1 = max(0, x1 - int(bw * 0.3))
    x2 = min(width, x2 + int(bw * 0.8))
    y1 = max(0, y1 - int(bh * 0.2))
    y2 = min(height, y2 + int(bh * 0.1))

    crop = image[y1:y2, x1:x2]

    if crop.size == 0:
        print("[NameResolver] EMPTY CROP")
        return None

    cv2.imwrite("debug_name_crop_original.png", crop)

    # 3x is enough; 8x just adds blur and a huge image
    crop = cv2.resize(crop, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    cv2.imwrite("debug_name_crop_image.png", crop)

    image_bytes = image_to_bytes(crop)

    if image_bytes is None:
        print("[NameResolver] Could not encode crop.")
        return None

    prompt = build_name_prompt(text)

    try:
        result = analyze_image(image_bytes, prompt)
    except Exception as e:
        print(f"[NameResolver] Gemma failed: {e}")
        return None

    parsed = parse_name_result(result)

    if parsed is None:
        print("[NameResolver] Could not parse Gemma result.")
        return None

    if not is_valid_reading(parsed["reading"]):
        print(f"[NameResolver] Rejected reading: {parsed['reading']!r}")
        return None

    print("[NameResolver] Resolved:")
    print(f"KANJI: {parsed['kanji']}")
    print(f"FURIGANA: {parsed['furigana']}")
    print(f"READING: {parsed['reading']}")

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
    
    return resolve_name_with_gemma(
        image,  
        text,
        box
    )