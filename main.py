from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes.scraper import router as scraper_router
from routes.translate_image import router as translator_image
app = FastAPI()
# url = "https://rawkuma.net/manga/deaimon/"
# url = "https://en.wikipedia.org/wiki/Nicol%C3%A1s_Maduro"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

headers = {
    "User-Agent": "MyLearningScraper/1.0"
}

app.mount(
    "/output",
    StaticFiles(directory="output"),
    name="output"
)
app.include_router(scraper_router)
app.include_router(translator_image)


    
   