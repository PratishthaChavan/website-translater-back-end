from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
# url = "https://rawkuma.net/manga/deaimon/"
# url = "https://en.wikipedia.org/wiki/Nicol%C3%A1s_Maduro"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
headers = {
    "User-Agent": "MyLearningScraper/1.0"
}
@app.post("/scraper")
def scrape_page(data: dict):
    
    url = data["url"]
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    texts = []

    for p in soup.find_all("p"):
        texts.append(p.get_text(strip=True))
    images = []

    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            images.append(urljoin(url, src))

    return {
        "title": soup.title.get_text(strip=True) if soup.title else "",
        "text": texts,
        "images": images
    }
