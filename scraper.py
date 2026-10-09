import os
import sys
import cv2
from PIL import Image

os.environ.setdefault(
    "HUB_DATASET_ENDPOINT",
    "https://modelscope.cn"
)

from paddleocr import PaddleOCR

sys.path.append("comic-text-detector")
from inference import TextDetector


# =========================================================
# IMAGE
# =========================================================

image_path = "images/deimon10.png"

image = cv2.imread(image_path)

if image is None:
    raise FileNotFoundError(image_path)


# =========================================================
# CTD
# =========================================================

detector = TextDetector(
    model_path="comic-text-detector/data/comictextdetector.pt.onnx",
    input_size=1024,
    device="cpu"
)

mask, mask_refined, blocks = detector(image)


# =========================================================
# PADDLE OCR
# =========================================================

ocr = PaddleOCR(
    lang="japan",
    enable_mkldnn=False
)


# =========================================================
# TEST EACH CTD BLOCK
# =========================================================

for i, block in enumerate(blocks):

    x1, y1, x2, y2 = map(
        int,
        block.xyxy
    )

    print()
    print("=" * 70)
    print(f"CTD BLOCK {i}")
    print("=" * 70)

    print(
        "CTD BOX:",
        [x1, y1, x2, y2]
    )


    # -----------------------------------------------------
    # Add padding
    # -----------------------------------------------------

    padding = 40

    cx1 = max(
        0,
        x1 - padding
    )

    cy1 = max(
        0,
        y1 - padding
    )

    cx2 = min(
        image.shape[1],
        x2 + padding
    )

    cy2 = min(
        image.shape[0],
        y2 + padding
    )


    # -----------------------------------------------------
    # Crop from ORIGINAL image
    # -----------------------------------------------------

    crop = image[
        cy1:cy2,
        cx1:cx2
    ]


    # -----------------------------------------------------
    # Save it
    # -----------------------------------------------------

    crop_path = f"ctd_block_{i}.png"

    cv2.imwrite(
        crop_path,
        crop
    )

    print(
        "Saved:",
        crop_path
    )


    # -----------------------------------------------------
    # Open the saved image with PIL
    # -----------------------------------------------------

    pil_image = Image.open(
        crop_path
    )

    print(
        "PIL SIZE:",
        pil_image.size
    )


    # -----------------------------------------------------
    # PaddleOCR receives PIL image
    # -----------------------------------------------------

    result = ocr.predict(
        pil_image
    )


    # -----------------------------------------------------
    # Print result
    # -----------------------------------------------------

    for res in result:

        print(res)