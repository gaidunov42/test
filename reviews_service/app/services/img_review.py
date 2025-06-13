from typing import List
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4
import shutil

from fastapi import UploadFile, HTTPException, Request


UPLOAD_DIR = Path("img")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_IMAGE_TYPES: set[str] = {"image/jpeg", "image/png", "image/webp", "image/gif"}


def save_uploaded_file(image: UploadFile) -> str:

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Недопустимый формат изображения: {image.content_type}",
        )

    filename = f"{uuid4().hex}_{image.filename}"
    file_path = UPLOAD_DIR / filename

    with file_path.open("wb") as f:
        shutil.copyfileobj(image.file, f)

    return str(file_path)


def get_file(reviews_list: list, request: Request) -> List[dict]:
    result = []

    for review in reviews_list:
        review["_id"] = str(review["_id"])

        image_path = review.get("image_path")
        if image_path:
            filename = Path(image_path).name
            review["image_url"] = str(request.url_for("img", path=quote(filename)))
        else:
            review["image_url"] = None

        review.pop("image_path", None)
        result.append(review)

    return result
