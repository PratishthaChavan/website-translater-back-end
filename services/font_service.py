import os


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


FONT_FILES = {
    "en": "NotoSans-Regular.ttf",
    "fr": "NotoSans-Regular.ttf",
    "es": "NotoSans-Regular.ttf",
    "de": "NotoSans-Regular.ttf",
    "pt": "NotoSans-Regular.ttf",

    "hi": "NotoSansDevanagari-Regular.ttf",

    "ar": "NotoSansArabic-Regular.ttf",

    "bn": "NotoSansBengali-Regular.ttf",

    "ta": "NotoSansTamil-Regular.ttf",

    "zh": "NotoSansCJK-Regular.ttc",
    "ja": "NotoSansCJK-Regular.ttc",
    "ko": "NotoSansCJK-Regular.ttc",
}


def get_font_path(target_language):
    font_file = FONT_FILES.get(
        target_language,
        "NotoSans-Regular.ttf"
    )

    return os.path.join(
        BASE_DIR,
        "fonts",
        font_file
    )