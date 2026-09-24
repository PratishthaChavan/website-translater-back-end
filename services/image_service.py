import cv2
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
from services.font_service import get_font_path
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def remove_text(image, mask_refined):
    return cv2.inpaint(
        image,
        mask_refined,
        3,
        cv2.INPAINT_TELEA
    )


def get_text_lines(draw, text, font, max_width):
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


def fit_text(draw, text, box_width, box_height,font_path):

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
            draw,
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
        draw,
        text,
        font,
        max_width
    )

    return font, lines, 11


def add_translated_text(
    clean_image,
    translated_texts,
    target_language
):

    font_path = get_font_path(
        target_language
    )

    clean_image_rgb = cv2.cvtColor(
        clean_image,
        cv2.COLOR_BGR2RGB
    )

    pil_image = Image.fromarray(
        clean_image_rgb
    )

    draw = ImageDraw.Draw(
        pil_image
    )

    for item in translated_texts:

        text = item["translation"]

        if not text:
            continue

        x1, y1, x2, y2 = item["box"]

        box_width = x2 - x1
        box_height = y2 - y1

        font, lines, line_height = fit_text(
            draw,
            text,
            box_width,
            box_height,
            font_path
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

    return cv2.cvtColor(
        np.array(pil_image),
        cv2.COLOR_RGB2BGR
    )
def save_translated_page(translated_image,manga_name,chapter_name,page_number):
    output_dir = os.path.join(
        "output",
        manga_name,
        chapter_name
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    filename = f"page_{page_number:03d}.png"

    output_path = os.path.join(
        output_dir,
        filename
    )

    success = cv2.imwrite(
        output_path,
        translated_image
    )

    if not success:
        raise IOError(
            f"Failed to save image: {output_path}"
        )

    return output_path