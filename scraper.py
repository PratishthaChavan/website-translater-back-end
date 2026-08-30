import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image

from paddleocr import PaddleOCR
url = "https://rawkuma.net/manga/deaimon/"
# url = "https://en.wikipedia.org/wiki/Nicol%C3%A1s_Maduro"

img_path = 'images/download.jpg'
ocr = PaddleOCR(
    lang="en"
)
result = ocr.predict(img_path)
for res in result:
    # print(res)
    texts = res['rec_texts']
    polys = res['rec_polys']
    scores = res['rec_scores']
    for text,poly,score in zip(texts,polys,scores):
        print("TEXT:", text)
        print("BOX:", poly)
        print("SCORE:", score)
        print("----------------")


headers = {
    "User-Agent": "MyLearningScraper/1.0"
}

response = requests.get(url, headers=headers)
# print(response)
soup = BeautifulSoup(response.text, "html.parser")
all_text = soup.find_all('p')
images = soup.find_all("img")
# print("\nNumber of images:", len(images))
for index, image in enumerate(images):
    src = image.get("src")
    alt = image.get('alt')
    # print(src)
    # print("this is image decription",alt)
    if not src:
        continue
    image_url = urljoin(url, src)

    # print(index, image_url)