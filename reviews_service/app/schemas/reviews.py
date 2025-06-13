from uuid import UUID
from typing import Union, Optional, List
from datetime import datetime

from fastapi import Form, File, UploadFile
from pydantic import BaseModel, Field


class ReviewPayload(BaseModel):
    product_id: int
    user_id: Optional[UUID]
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    image_path: Optional[str] = None
    created_at: Optional[datetime] = None


class ReviewForm:
    def __init__(
        self,
        product_id: str = Form(...),
        user_id: UUID = Form(None),
        rating: int = Form(...),
        comment: str = Form(None),
        image: UploadFile = File(None),
    ):
        self.payload = ReviewPayload(
            product_id=product_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
        )
        self.image = image


class ReviewResponse(BaseModel):
    id: str = Field(..., alias="_id")
    product_id: Union[int, str]
    user_id: Optional[UUID]
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    image_url: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True


class ReviewListResponse(BaseModel):
    product_id: Union[int, str]
    reviews: List[ReviewResponse]
