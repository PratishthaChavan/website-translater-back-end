import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin,urlparse
from collections import defaultdict
import re
headers = {
    "User-Agent": "MyLearningScraper/1.0"
}

LAZY_ATTRS = ["src", "data-src", "data-lazy-src", "data-original", "data-url"]

JUNK_PATTERNS = re.compile(
    r"(logo|avatar|icon|favicon|banner|ads?|sprite|thumb|thumbnail|"
    r"placeholder|loading|spinner|profile|user|flag|button|share|social)",
    re.IGNORECASE
)

BAD_EXTENSIONS = (".svg", ".gif", ".ico")

def get_image_url(img, page_url):
    for attr in LAZY_ATTRS:
        value = img.get(attr)
        if value and not value.startswith("data:"):
            return urljoin(page_url, value.strip())

    srcset = img.get("srcset")
    if srcset:
        # take the last (usually largest) candidate
        candidate = srcset.split(",")[-1].strip().split(" ")[0]
        if candidate:
            return urljoin(page_url, candidate)

    return None


def looks_like_junk(image_url):
    path = urlparse(image_url).path.lower()

    if path.endswith(BAD_EXTENSIONS):
        return True

    if JUNK_PATTERNS.search(path):
        return True

    return False

def get_reader_images(soup, page_url):
    groups = defaultdict(list)

    for img in soup.find_all("img"):
        image_url = get_image_url(img, page_url)

        if not image_url or looks_like_junk(image_url):
            continue

        parent = img.find_parent(["div", "section", "article", "main", "p"])
        key = id(parent) if parent is not None else 0
        groups[key].append(image_url)

    if not groups:
        return []

    best = max(groups.values(), key=len)

    seen = set()
    ordered = []
    for url in best:
        if url not in seen:
            seen.add(url)
            ordered.append(url)

    return ordered

def scrape_page(url):
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    chapter_info = get_chapter_info(soup)

    images = get_reader_images(soup, url)

    if not images:
        print(f"No page images found for {url}")

    return {
        "title": chapter_info["title"],
        "manga_name": chapter_info["manga_name"],
        "chapter_number": chapter_info["chapter_number"],
        "images": images
    }
    
def get_chapter_info(soup, url=None):
    title = soup.title.get_text(" ", strip=True) if soup.title else ""

    chapter_match = re.search(
        r"chapter[\s-]*(\d+(?:\.\d+)?)",
        title,
        re.IGNORECASE
    )

    chapter_number = chapter_match.group(1) if chapter_match else None

    # fallback: pull chapter number from the URL path, e.g. /chapter-29/
    if chapter_number is None and url:
        url_match = re.search(
            r"chapter[\s\-_/]*(\d+(?:\.\d+)?)",
            urlparse(url).path,
            re.IGNORECASE
        )
        if url_match:
            chapter_number = url_match.group(1)

    manga_name = re.sub(
        r"\s*chapter[\s-]*\d+(?:\.\d+)?[\s\S]*$",
        "",
        title,
        flags=re.IGNORECASE
    ).strip()

    return {
        "title": title,
        "manga_name": manga_name,
        "chapter_number": chapter_number
    }