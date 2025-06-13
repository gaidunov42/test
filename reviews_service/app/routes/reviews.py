from bson import ObjectId
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from app.mongo.mongo_client import Mongo
from app.schemas.reviews import (
    ReviewForm,
    ReviewListResponse,
)
from app.services.img_review import save_uploaded_file, get_file
from app.kafka.kafka_client import produce_kafka_message
from app.services.check_token_service import require_access_token, require_permission


reviews = APIRouter(prefix="/reviews", tags=["Работа с отзывами"])


@reviews.get(
    "/{product_id}",
    summary="Посмотреть все комментарии по id продукта",
    response_model=ReviewListResponse,
)
@require_access_token
@require_permission("user.user")
async def get_reviews(request: Request, product_id: int):
    async with Mongo() as db:
        cursor = db["reviews"].find({"product_id": product_id})
        cursor = cursor.sort("created_at", -1)
        reviews_list = await cursor.to_list(length=None)
    if not reviews_list:
        raise HTTPException(status_code=404, detail="Отзывы не найдены")

    reviews_list = get_file(reviews_list, request)

    return {"product_id": product_id, "reviews": reviews_list}


@reviews.post("/", summary="Создать новый комментарий")
@require_access_token
@require_permission("user.user")
async def create_review(request: Request, form: ReviewForm = Depends()) -> dict:
    payload = form.payload
    image = form.image

    image_path = save_uploaded_file(image) if image else None

    review_data = payload.model_dump()
    review_data["image_path"] = image_path
    review_data["created_at"] = datetime.now(timezone.utc)
    async with Mongo() as db:
        result = await db["reviews"].insert_one(review_data)
        review_data["_id"] = str(result.inserted_id)
    await produce_kafka_message(value={"event": "REVIEW_CREATED", "data": review_data})
    return {"message": "Review created", "data": review_data}


@reviews.delete("/{id}", summary="Удалить коментарий по id")
@require_access_token
@require_permission("admin.admin")
async def delete_review(request: Request, id: str) -> dict:
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Неверный формат ID")

    async with Mongo() as db:
        result = await db["reviews"].delete_one({"_id": ObjectId(id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Отзыв не найден")

    return {"message": f"Отзыв {id} удалён"}
