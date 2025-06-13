from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.schemas import CategoryPayload, SCategory
from app.crud.categories import Category
from app.services.cache_service import cash
from app.services.check_token_service import require_access_token, require_permission


categories = APIRouter(prefix="/categories", tags=["Работа с категориями"])


@categories.get("/", summary="Получить все категории", response_model=list[SCategory])
async def get_categories():
    try:
        categories_data = await cash.get_value("categories_list")
        if categories_data:
            return categories_data
        categories = await Category.find_all()
        await cash.set_value("categories_list", categories)
        return categories
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при выполнении запроса")


@categories.get("/{category_id}", summary="Получить категорию по по category_id")
async def get_products_by_id(category_id: int) -> SCategory | dict:
    try:
        result = await Category.find_one_or_none_by_id(category_id)
        if result is None:
            return HTTPException(
                status_code=404, detail=f"Категория с ID {category_id} не найдена!"
            )
        return result
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при выполнении запроса")


@categories.post("/", summary="Добавить категорию", status_code=201)
@require_access_token
@require_permission("manager.manager")
async def add_category(request: Request, payload: CategoryPayload) -> SCategory | dict:
    try:
        result = await Category.add(**payload.model_dump())
        categories = await Category.find_all()
        await cash.set_value("categories_list", categories)
        if not result:
            raise HTTPException(
                status_code=404, detail="Ошибка при добавлении категории!"
            )
        return result
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при добавлении категории")


@categories.put("/{category_id}", summary="Обновить категорию по id", status_code=201)
@require_access_token
@require_permission("manager.manager")
async def put_category(request: Request, category_id: int, payload: CategoryPayload):
    try:
        result = await Category.update_category(category_id, **payload.model_dump())
        categories = await Category.find_all()
        await cash.set_value("categories_list", categories)
        if not result:
            return HTTPException(
                status_code=404, detail="Ошибка при обновлении категории!"
            )
        return {"message": "Категория успешно обновлена", "Категория": payload}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при выполнении запроса")


@categories.delete("/{category_id}", summary="Удалить категорию по id")
@require_access_token
@require_permission("manager.manager")
async def delete_product(
    request: Request,
    category_id: int,
):
    try:
        result = await Category.delete_category(category_id)
        categories = await Category.find_all()
        await cash.set_value("categories_list", categories)
        if not result:
            return HTTPException(
                status_code=404, detail="Ошибка при удалении категории!"
            )
        return {"message": "Категория успешно удалена", "Категория": category_id}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при выполнении запроса")
