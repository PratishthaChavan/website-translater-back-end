import sys
import cv2
import torch
from PIL import Image, ImageDraw, ImageFont
from manga_ocr import MangaOcr
sys.path.append("comic-text-detector")

from inference import TextDetector
from paddleocr import PaddleOCR
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


image_path = "images/deimon4.png"

image = cv2.imread(image_path)

if image is None:
    raise FileNotFoundError(image_path)


detector = TextDetector(
    model_path="comic-text-detector/data/comictextdetector.pt.onnx",
    input_size=1024,
    device="cpu"
)

mask, mask_refined, blocks = detector(image)

print("Detected blocks:", len(blocks))


ocr = MangaOcr()


model_name = "facebook/nllb-200-distilled-600M"

tokenizer = AutoTokenizer.from_pretrained(model_name)
translator = AutoModelForSeq2SeqLM.from_pretrained(model_name)

tokenizer.src_lang = "jpn_Jpan"


def translate_text(text):
    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512
    )

    with torch.no_grad():
        output = translator.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids("eng_Latn"),
            max_length=256,
            num_beams=5,
            repetition_penalty=1.1,
            no_repeat_ngram_size=2
        )

    return tokenizer.batch_decode(
        output,
        skip_special_tokens=True
    )[0].strip()


clean_image = cv2.inpaint(
    image,
    mask_refined,
    3,
    cv2.INPAINT_TELEA
)


clean_image_rgb = cv2.cvtColor(
    clean_image,
    cv2.COLOR_BGR2RGB
)

pil_image = Image.fromarray(clean_image_rgb)
draw = ImageDraw.Draw(pil_image)


font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def get_text_lines(text, font, max_width):
    words = text.split()

    if not words:
        return []

    lines = []
    current_line = ""

    for word in words:
        test_line = (
            current_line + " " + word
        ).strip()

        bbox = draw.textbbox(
            (0, 0),
            test_line,
            font=font
        )

        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)

            current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def fit_text(text, box_width, box_height):

    padding_x = max(8, int(box_width * 0.08))
    padding_y = max(5, int(box_height * 0.08))

    max_width = box_width - padding_x * 2
    max_height = box_height - padding_y * 2

    starting_size = max(
        12,
        min(
            26,
            int(box_height * 0.22)
        )
    )

    for font_size in range(starting_size, 9, -1):

        font = ImageFont.truetype(
            font_path,
            font_size
        )

        lines = get_text_lines(
            text,
            font,
            max_width
        )

        line_height = int(font_size * 1.15)
        total_height = len(lines) * line_height

        if total_height <= max_height:
            return font, lines, line_height

    font = ImageFont.truetype(
        font_path,
        9
    )

    lines = get_text_lines(
        text,
        font,
        max_width
    )

    return font, lines, 11

for i, block in enumerate(blocks):

    x1, y1, x2, y2 = map(int, block.xyxy)

    crop = image[y1:y2, x1:x2]

    crop_rgb = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2RGB
    )

    crop_pil = Image.fromarray(crop_rgb)

    source_text = ocr(crop_pil)

    if not source_text:
        continue

    source_text = source_text.strip()

    translated_text = translate_text(source_text)

    if not translated_text:
        continue

    print("\nBlock", i + 1)
    print("Japanese:", source_text)
    print("English:", translated_text)

    box_width = x2 - x1
    box_height = y2 - y1

    font, lines, line_height = fit_text(
        translated_text,
        box_width,
        box_height
    )

    total_height = len(lines) * line_height

    start_y = (
        y1 +
        (box_height - total_height) // 2
    )

    for line in lines:

        bbox = draw.textbbox(
            (0, 0),
            line,
            font=font
        )

        text_width = bbox[2] - bbox[0]

        text_x = (
            x1 +
            (box_width - text_width) // 2
        )

        text_y = (
            start_y -
            bbox[1]
        )

        draw.text(
            (text_x, text_y),
            line,
            font=font,
            fill="black"
        )

        start_y += line_height
output_path = "output/translated7.png"
pil_image.save(output_path)