import sys
import cv2
import torch
from PIL import Image, ImageDraw, ImageFont

sys.path.append("comic-text-detector")

from inference import TextDetector
from manga_ocr import MangaOcr
from transformers import AutoTokenizer, AutoModelForCausalLM


model_name = "fumetodev/Hy-MT2-1.8B-JP-Manga-Finetune-v5-GGUF"
tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    trust_remote_code=True
)

translator = AutoModelForCausalLM.from_pretrained(
    model_name,
    trust_remote_code=True,
    device_map="auto"
)


image_path = "images/deimon7.png"

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


def translate_text(text):

    prompt = (
        "Reference information:\n"
        "和む（なごむ） is the character name Nagomu.\n\n"
        "Translate the following Japanese manga dialogue "
        "into natural, concise English. "
        "Preserve character names, tone, emotion, "
        "speaker intent, dialect, and meaning. "
        "Output only the translated dialogue.\n\n"
        f"{text}"
    )

    inputs = tokenizer(
        prompt,
        return_tensors="pt"
    )

    inputs.pop("token_type_ids", None)

    inputs = inputs.to(translator.device)
    with torch.no_grad():
        outputs = translator.generate(
            **inputs,
            max_new_tokens=80,
            do_sample=False,
            repetition_penalty=1.05
        )

    generated_tokens = outputs[
        0,
        inputs["input_ids"].shape[-1]:
    ]

    return tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True
    ).strip()


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

    padding_x = max(
        8,
        int(box_width * 0.08)
    )

    padding_y = max(
        5,
        int(box_height * 0.08)
    )

    max_width = box_width - padding_x * 2
    max_height = box_height - padding_y * 2

    starting_size = max(
        12,
        min(
            26,
            int(box_height * 0.22)
        )
    )

    for font_size in range(
        starting_size,
        9,
        -1
    ):

        font = ImageFont.truetype(
            font_path,
            font_size
        )

        lines = get_text_lines(
            text,
            font,
            max_width
        )

        line_height = int(
            font_size * 1.15
        )

        total_height = (
            len(lines) * line_height
        )

        if total_height <= max_height:

            return (
                font,
                lines,
                line_height
            )

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

    x1, y1, x2, y2 = map(
        int,
        block.xyxy
    )

    crop = image[
        y1:y2,
        x1:x2
    ]

    if crop.size == 0:
        continue

    crop_rgb = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2RGB
    )

    crop_pil = Image.fromarray(
        crop_rgb
    )

    source_text = ocr(
        crop_pil
    ).strip()

    if not source_text:
        continue

    translated_text = translate_text(
        source_text
    )

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

    total_height = (
        len(lines) * line_height
    )

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

        text_width = (
            bbox[2] - bbox[0]
        )

        text_x = (
            x1 +
            (box_width - text_width) // 2
        )

        text_y = (
            start_y - bbox[1]
        )

        draw.text(
            (text_x, text_y),
            line,
            font=font,
            fill="black"
        )

        start_y += line_height

output_path = "output/translated5.png"

pil_image.save(output_path)

print("\nSaved:", output_path)