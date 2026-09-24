import os
import uuid
import shutil

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    BackgroundTasks,
    Form
)

from services.job_service import create_job
from services.upload_service import process_uploaded_images


router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


@router.post("/translate/images")
async def translate_uploaded_images(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    target_language: str = Form("en")
):

    if not files:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least one image."
        )

    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="You can upload up to 10 images."
        )

    job_id = create_job()

    job_upload_dir = os.path.join(
        UPLOAD_DIR,
        job_id
    )

    os.makedirs(
        job_upload_dir,
        exist_ok=True
    )

    input_paths = []

    for index, file in enumerate(files, start=1):

        if not file.content_type:
            raise HTTPException(
                status_code=400,
                detail="Invalid file."
            )

        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="Only image files are allowed."
            )

        extension = os.path.splitext(
            file.filename or ""
        )[1].lower()

        if not extension:
            extension = ".png"

        filename = f"image_{index:03d}{extension}"

        input_path = os.path.join(
            job_upload_dir,
            filename
        )

        with open(
            input_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        input_paths.append(input_path)

    background_tasks.add_task(
        process_uploaded_images,
        input_paths,
        job_id,
        target_language
    )

    return {
        "job_id": job_id
    }