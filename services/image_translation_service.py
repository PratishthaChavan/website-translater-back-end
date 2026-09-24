import cv2
import time

from services.ocr_service import detect_text, extract_text
from services.translator_service import text_translator
from services.image_service import remove_text, add_translated_text


def translate_image(image, target_language):

    if image is None:
        raise ValueError("Invalid image")

    start = time.perf_counter()

    t = time.perf_counter()

    ocr_result = detect_text(image)

    print(
        f"CTD: {time.perf_counter() - t:.2f}s"
    )

    t = time.perf_counter()

    texts = extract_text(
        image,
        ocr_result["blocks"]
    )
    print("this is the text",texts)
    print(
        f"OCR: {time.perf_counter() - t:.2f}s"
    )

    print(
        f"Text blocks: {len(texts)}"
    )

    if not texts:
        return image

    t = time.perf_counter()

    clean_image = remove_text(
        image,
        ocr_result["mask_refined"]
    )

    print(
        f"Inpainting: {time.perf_counter() - t:.2f}s"
    )

    t = time.perf_counter()

    translated_texts = text_translator(
        texts,
        target_language
    )

    print(
        f"Translation: {time.perf_counter() - t:.2f}s"
    )

    t = time.perf_counter()

    translated_image = add_translated_text(
        clean_image,
        translated_texts,
        target_language
    )

    print(
        f"Rendering: {time.perf_counter() - t:.2f}s"
    )

    print(
        f"TOTAL: {time.perf_counter() - start:.2f}s"
    )

    return translated_image