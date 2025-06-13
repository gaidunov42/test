from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.schemas import ProductsPayload, SProduct
from app.crud.products import Product
from app.kafka.kafka_client import produce_kafka_message
from app.services.check_token_service import require_access_token, require_permission


products = APIRouter(prefix="/products", tags=["Работа с Позициями"])


@products.get("/", summary="Получить все продукты", response_model=list[SProduct])
async def get_products():
    try:
        return await Product.find_product_all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при выполнении запроса")


@products.get("/{product_id}", summary="Получить позиции по id")
async def get_products_by_id(product_id: int) -> SProduct | dict:
    try:
        product = await Product.find_product_one_or_none_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Продукт не найден")
        return product
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при выполнении запроса")


@products.post("/", summary="Добавить новую позицию", status_code=201)
@require_access_token
@require_permission("manager.manager")
async def add_product(request: Request, payload: ProductsPayload):
    try:
        product = await Product.add(**payload.model_dump())
        if not product:
            HTTPException(status_code=404, detail="Ошибка при добавлении позиции!")
        return {"message": "Позиция успешно добавлена", "Позиция": payload}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при добавлении позиции")


@products.put("/{product_id}", summary="Изменить определенную позицию", status_code=201)
@require_access_token
@require_permission("manager.manager")
async def put_product(request: Request, product_id: int, payload: ProductsPayload):
    try:
        data = payload.model_dump(exclude_none=True)
        if not data:
            raise HTTPException(status_code=400, detail="Нет данных для обновления")
        updated = await Product.update_product(product_id, **data)
        if not updated:
            return HTTPException(
                status_code=404, detail=f"Продукт {product_id} не найден"
            )
        await produce_kafka_message(
            value={"event": "PRODUCT_UPDATED", "product_id": product_id}
        )
        return {"message": "Продукт обновлён"}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при выполнении запроса")


@products.delete("/{product_id}", summary="Удалить определенную позицию")
@require_access_token
@require_permission("manager.manager")
async def delete_product(request: Request, product_id: int):
    try:
        result = await Product.delete_by_id(product_id)
        if not result:
            return HTTPException(status_code=404, detail="Ошибка при удалении позиции!")
        return {"message": "Позиция успешно удалена", "Позиция": product_id}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при выполнении запроса")
