import sys
import cv2

from manga_ocr import MangaOcr
from PIL import Image

sys.path.append("comic-text-detector")

from inference import TextDetector


ocr = MangaOcr()

detector = TextDetector(
    model_path="comic-text-detector/data/comictextdetector.pt.onnx",
    input_size=1024,
    device="cpu"
)


def detect_text(image):
    print("Detecting text in image...")

    mask, mask_refined, blocks = detector(image)

    print(
        f"CTD detected {len(blocks)} blocks"
    )

    return {
        "mask": mask,
        "mask_refined": mask_refined,
        "blocks": blocks
    }


def extract_text(image, blocks):

    results = []

    height, width = image.shape[:2]

    for i, block in enumerate(blocks):

        print(
            f"\n========== BLOCK {i + 1} =========="
        )

        x1, y1, x2, y2 = map(
            int,
            block.xyxy
        )

        print(
            "Original box:",
            (x1, y1, x2, y2)
        )

        # ------------------------------------------
        # Clamp coordinates
        # ------------------------------------------

        x1 = max(
            0,
            min(x1, width - 1)
        )

        y1 = max(
            0,
            min(y1, height - 1)
        )

        x2 = max(
            0,
            min(x2, width)
        )

        y2 = max(
            0,
            min(y2, height)
        )

        print(
            "Clamped box:",
            (x1, y1, x2, y2)
        )

        if x2 <= x1 or y2 <= y1:

            print("INVALID BOX")

            continue

        # ------------------------------------------
        # Crop text region
        # ------------------------------------------

        crop = image[
            y1:y2,
            x1:x2
        ]

        print(
            "Crop shape:",
            crop.shape
        )

        if crop.size == 0:

            print("EMPTY CROP")

            continue

        # ------------------------------------------
        # Convert BGR → RGB
        # ------------------------------------------

        crop_rgb = cv2.cvtColor(
            crop,
            cv2.COLOR_BGR2RGB
        )

        crop_pil = Image.fromarray(
            crop_rgb
        )

        # ------------------------------------------
        # MangaOCR
        # ------------------------------------------

        source_text = ocr(
            crop_pil
        ).strip()

        print(
            "MangaOCR:",
            repr(source_text)
        )

        if not source_text:

            print(
                "OCR RETURNED EMPTY → BLOCK DROPPED"
            )

            continue

        # ------------------------------------------
        # Save result
        # ------------------------------------------

        results.append({
            "text": source_text,
            "box": [
                x1,
                y1,
                x2,
                y2
            ]
        })

    return results