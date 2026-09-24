import requests
import numpy as np
import cv2
import os
import re

from services.image_service import save_translated_page
from services.job_service import complete_job, add_page
from services.image_translation_service import translate_image
from services.scraper_service import scrape_page


headers = {
    "User-Agent": "MyLearningScraper/1.0"
}


MIN_WIDTH = 400
MIN_HEIGHT = 400
MIN_RATIO = 0.5


def is_manga_page(image):

    height, width = image.shape[:2]

    if width < MIN_WIDTH or height < MIN_HEIGHT:
        return False

    if height / width < MIN_RATIO:
        return False

    return True


def download_image(image_url):
    try:
        response = requests.get(
            image_url,
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:

            print(
                f"Skipping {image_url} "
                f"Status: {response.status_code}"
            )

            return None

        image_array = np.frombuffer(
            response.content,
            dtype=np.uint8
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if image is None:

            print(
                f"Could not decode image: {image_url}"
            )

            return None
        print(
            "Downloaded image:",
            image.shape,
            "bytes:",
            len(response.content)
        )

        return image
    except requests.RequestException as e:

        print(
            f"Failed to download image: {e}"
        )

        return None


def translate_chapter(
    url,
    job_id,
    target_language
):

    page_data = scrape_page(url)

    manga_name = page_data["manga_name"]

    chapter_name = (
        f"chapter_{page_data['chapter_number']}"
    )

    if chapter_exists(
        manga_name,
        chapter_name
    ):

        print(
            f"Chapter already exists: "
            f"{manga_name}/{chapter_name}"
        )

        saved_pages = get_saved_pages(
            manga_name,
            chapter_name
        )

        for index, page_url in enumerate(
            saved_pages,
            start=1
        ):

            add_page(
                job_id,
                index,
                page_url
            )

        complete_job(job_id)
        return
    image_urls = page_data["images"]
    page_number = 1
    for image_url in image_urls:
        image = download_image(
            image_url
        )
        if image is None:
            continue
        if not is_manga_page(image):
            print(
                f"Skipping non-page image: "
                f"{image_url}"
            )
            continue

        translated_image = translate_image(
            image,
            target_language
        )

        output_path = save_translated_page(
            translated_image,
            manga_name,
            chapter_name,
            page_number
        )

        page_url = "/" + output_path.replace(
            "\\",
            "/"
        )

        add_page(
            job_id,
            page_number,
            page_url
        )

        page_number += 1

    complete_job(job_id)


def chapter_exists(
    manga_name,
    chapter_name
):

    saved_pages = get_saved_pages(
        manga_name,
        chapter_name
    )

    return len(saved_pages) > 0


def get_saved_pages(
    manga_name,
    chapter_name
):

    chapter_path = os.path.join(
        "output",
        manga_name,
        chapter_name
    )

    if not os.path.isdir(
        chapter_path
    ):

        return []

    files = [
        file
        for file in os.listdir(
            chapter_path
        )
        if re.match(
            r"^page_\d{3}\.png$",
            file
        )
    ]

    files.sort()

    pages = [
        "/" + os.path.join(
            "output",
            manga_name,
            chapter_name,
            file
        ).replace(
            "\\",
            "/"
        )
        for file in files
    ]

    print(
        "Chapter folder:",
        chapter_path
    )

    print(
        "Saved pages:",
        pages
    )

    return pages