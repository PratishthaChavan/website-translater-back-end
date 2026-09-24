from fastapi import APIRouter,BackgroundTasks
from services.scraper_service import scrape_page
from fastapi.responses import StreamingResponse

from services.job_service import create_job,jobs
from services.chapter_service import translate_chapter
import asyncio
import json
router = APIRouter()

# @router.post("/scraper")
# def scraper(data: dict):
#     url = data["url"]

#     return scrape_page(url)

@router.post("/scraper")
def translate(data: dict,background_tasks: BackgroundTasks):
    job_id = create_job()

    url = data["url"]
    target_language = data["target_language"]
    background_tasks.add_task(translate_chapter,url,job_id,target_language)

    # return translate_chapter(url)
    return {
        "job_id":job_id
    }
@router.get("/translate/stream/{job_id}")
async def translation_stream(job_id: str):

    async def event_generator():

        try:
            while True:

                if job_id not in jobs:
                    yield (
                        "event: error\n"
                        'data: {"message":"Job not found"}\n\n'
                    )
                    return

                job = jobs[job_id]

                while job["pages"]:
                    page = job["pages"].pop(0)

                    print("SSE sending:", page)

                    yield (
                        "event: page\n"
                        f"data: {json.dumps(page)}\n\n"
                    )

                if job["complete"]:
                    yield (
                        "event: complete\n"
                        f"data: {json.dumps({'status': 'completed'})}\n\n"
                    )
                    return

                yield ": heartbeat\n\n"

                await asyncio.sleep(0.5)

        except asyncio.CancelledError:
            print("SSE client disconnected")
            raise

        except Exception as e:
            print("SSE error:", e)

            yield (
                "event: error\n"
                f"data: {json.dumps({'message': str(e)})}\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )