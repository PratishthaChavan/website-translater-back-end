import os
import cv2
import boto3
from dotenv import load_dotenv
load_dotenv()

S3_BUCKET = os.getenv("S3_BUCKET")
AWS_REGION = os.getenv(
    "AWS_REGION",
    "ap-south-1"
)

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION
)
def upload_image(image,object_key):
    success, encoded = cv2.imencode(
        ".png",
        image
    )
    if not success:
        raise RuntimeError(
            "Could not encode image"
        )
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=object_key,
        Body=encoded.tobytes(),
        ContentType="image/png"
    )
    return object_key


def get_saved_pages(manga_name,chapter_name):
    prefix = (
        f"manga/"
        f"{manga_name}/"
        f"{chapter_name}/"
    )

    response = s3_client.list_objects_v2(
        Bucket=S3_BUCKET,
        Prefix=prefix
    )

    pages = {}
    for item in response.get("Contents", []):
        key = item["Key"]
        filename = key.split("/")[-1]
        if not filename.startswith("page_"):
            continue
        if not filename.endswith(".png"):
            continue
        try:

            page_number = int(
                filename[
                    len("page_"):-len(".png")
                ]
            )

        except ValueError:
            continue

        pages[page_number] = key
    return pages

def get_presigned_url(
    object_key,
    expires_in=3600
):
    return s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": object_key
        },
        ExpiresIn=expires_in
    )