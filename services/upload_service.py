import os
import cv2

from services.image_translation_service import translate_image
from services.image_service import save_translated_page
from services.job_service import (
    add_page,
    complete_job
)


def process_uploaded_images(
    input_paths,
    job_id,
    target_language
):

    try:
        page_number = 1
        for input_path in input_paths:
            image = cv2.imread(
                input_path
            )

            if image is None:
                continue

            translated_image = translate_image(
                image,
                target_language
            )

            output_path = save_translated_page(
                translated_image,
                "uploads",
                job_id,
                page_number
            )

            page_url = "/" + output_path.replace(
                "\\",
                "/"
            )

            add_page(job_id,page_number,page_url)

            page_number += 1

            os.remove(
                input_path
            )

    except Exception as e:

        print(
            "Image translation failed:",
            e
        )

    finally:

        for input_path in input_paths:

            if os.path.exists(input_path):
                os.remove(input_path)

        complete_job(job_id)