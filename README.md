Manga / Webtoon Translator

A web-based manga and webtoon translation application that accepts a webpage URL or uploaded manga images, detects the text, translates it, removes the original text, and places the translated text back into the image.

Purpose

The project is designed to automate manga page translation while preserving the original artwork and text positions as much as possible.

It supports two main inputs:

Manga chapter webpage URL

Uploaded manga images

Main Processing Flow

URL / Uploaded Image
        ↓
Scrape or Upload
        ↓
Download / Read Image
        ↓
Detect Text
        ↓
Extract Text with OCR
        ↓
Translate Text
        ↓
Remove Original Text
        ↓
Render Translated Text
        ↓
Save Translated Image
        ↓
Send Page through Job / SSE
        ↓
Frontend

Services

1. scraper_service.py

Responsible for extracting manga/chapter information and page image URLs from a webpage.

get_image_url()
Purpose: Gets the actual image URL from an HTML <img> element.
Uses: BeautifulSoup, urljoin, lazy-loading attributes, and srcset.
Flow <img> tag → check image attributes → build full URL → return image URL.

looks_like_junk()
Purpose: Filters images that are probably not manga pages.
Uses: urlparse, regex patterns, and unwanted file extensions.
Flow: Image URL → check extensions/keywords → accept or reject.

get_reader_images()
Purpose: Finds the manga page images from the webpage.
Uses: BeautifulSoup, get_image_url(), looks_like_junk(), and defaultdict.
Flow: Find <img> tags → filter unwanted images → select the largest image group → remove duplicates → return ordered URLs.

get_chapter_info()
Purpose: Extracts the manga name and chapter number.
Uses: BeautifulSoup, regex, and URL parsing.
Flow: Page title/URL → find chapter number → extract manga name → return chapter information

scrape_page()
Purpose: Main scraper function that collects chapter information and image URLs.
Uses: requests, BeautifulSoup, get_chapter_info(), and get_reader_images().
Flow: URL → download HTML → parse page → get chapter info + image URLs → return chapter data.

2. chapter_service.py

Responsible for downloading, translating, saving, and tracking all pages of a manga chapter.

is_manga_page()
Purpose: Checks whether a downloaded image is suitable for manga processing.
Uses: OpenCV image dimensions and aspect ratio.
Flow: Image → check width/height/ratio → process or skip.

download_image()
Purpose: Downloads a manga page image into memory for processing.
Uses: requests, NumPy, and OpenCV.
Flow: Image URL → download bytes → NumPy array → OpenCV decoding → return image.

translate_chapter()
Purpose: Runs the complete translation process for all pages in a chapter.
Uses: scraper_service, image_translation_service, image_service, and job_service.
Flow: URL → scrape pages → download image → validate → translate → save → notify job → continue to next page.

chapter_exists()
Purpose: Checks whether a translated chapter is already stored.
Uses: get_saved_pages() and the file system.
Flow: Manga + chapter → check saved pages → return True or False.

get_saved_pages()
Purpose: Gets previously translated pages from a chapter folder.
Uses: os, regex, and the file system.
Flow: Chapter folder → find saved page files → sort pages → return page URLs.

3. ocr_service.py

Responsible for detecting text regions and extracting text from manga images.

detect_text()
Purpose: Detects where text is located inside a manga image.
Uses: Comic Text Detector (CTD), ONNX model, and OpenCV.
Flow: Image → CTD → detect text blocks + masks → return detection result.

extract_text()
Purpose: Extracts readable text from detected text regions.
Uses: MangaOCR, OpenCV, and PIL.
Flow: Text block → crop image → OCR → return text + coordinates.

4. translator_service.py

Responsible for translating the text extracted by OCR.

translate_with_llama()
Purpose: Sends the translation request to the local language model server.
Uses: requests and the local llama.cpp API.
Flow: Prompt → HTTP request → Gemma model → translated response.

text_translator()
Purpose: Translates all OCR text blocks from a manga page.
Uses: Gemma 3 GGUF running through llama.cpp.
Flow: OCR text → build page context → send translation request → return translated text blocks.

5. image_service.py

Responsible for removing the original text, rendering translated text, and saving translated pages.

remove_text()
Purpose: Removes the original text from the image.
Uses: OpenCV inpainting and the detected text mask.
Flow: Image + mask → inpainting → cleaned image.

add_translated_text()
Purpose: Places translated text into the original text regions.
Uses: PIL, ImageDraw, ImageFont, text wrapping, and font fitting.
Flow: Clean image + translated text + coordinates → fit text → draw text → final image.

fit_text()
Purpose: Finds a font size that allows translated text to fit inside its text box.
Uses: PIL font measurement
Flow: Text + box dimensions → test font sizes → select a suitable size.

save_translated_page()
Purpose: Saves the final translated manga page to the output directory.
Uses: OpenCV and the file system.
Flow: Translated image → create output directory → save PNG → return output path.

6. image_translation_service.py

Connects OCR, translation, and image processing into one reusable pipeline

translate_image()
Purpose: Translates one manga image from start to finish.
Uses: ocr_service, translator_service, and image_service.
Flow: Image → detect text → extract text → translate → remove original text → render translation → return final image.

7. job_service.py
Responsible for tracking translation jobs and completed pages.

create_job()
Purpose: Creates a unique job for a translation request.
Uses: Python uuid and in-memory job storage.
Flow: Translation request → generate job ID → create job state.

add_page()
Purpose: Adds a completed page to a running translation job.
Uses: In-memory job dictionary.
Flow: Page completed → store page number + URL → page becomes available to the SSE stream.

complete_job()
Purpose: Marks a translation job as completed.
Uses: In-memory job dictionary.
Flow: All pages processed → update job status → SSE sends completion event.

8. upload_service.py

Responsible for processing uploaded manga images in the background.

process_uploaded_images()
Purpose: Processes uploaded images using the same image translation pipeline.
Uses: OpenCV, translate_image(), save_translated_page(), and job_service.
Flow: Temporary uploaded image → read image → translate → save result → notify job → delete temporary input.

9. font_service.py

Responsible for selecting the correct font for the target language.

get_font_path()
Purpose: Returns the appropriate font file for the selected language.
Uses: Project-local Noto fonts and language-to-font mapping.
Flow: Language code → find matching font → return font path.


Key Technologies

FastAPI — backend API
React — frontend
Requests — HTTP requests and local LLM API calls
BeautifulSoup — webpage parsing
OpenCV — image processing and inpainting
NumPy — image byte conversion and array processing
Comic Text Detector (CTD) — manga text detection
MangaOCR — Japanese manga text recognition
Gemma 3 GGUF — text translation
llama.cpp — local LLM inference server
Pillow (PIL) — translated text rendering
SSE — sends completed translated pages to the frontend progressively
