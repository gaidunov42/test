from uuid import UUID

from fastapi import APIRouter, HTTPException, Request

from app.schemas.schemas import (
    NewOrderPayload,
    OrderCreateResponse,
    UserOrdersResponse,
    OrderResponse,
    OrderUpdatePayload,
)
from app.crud.orders import OrderService
from app.kafka.kafka_client import produce_kafka_message
from app.services.check_token_service import require_access_token, require_permission


orders = APIRouter(prefix="/orders", tags=["Работа с заказами"])


@orders.get(
    "/by_user/{user_id}",
    summary="Получить все заказы пользователя",
    response_model=UserOrdersResponse,
)
@require_access_token
@require_permission("user.user")
async def get_order_by_user_id(request: Request, user_id: UUID):
    orders = await OrderService.get_user_orders(user_id)
    if not orders:
        raise HTTPException(status_code=404, detail="Заказы не найдены")
    return UserOrdersResponse(orders=orders)


@orders.get(
    "/by_order/{order_id}", summary="Получить заказ по id", response_model=OrderResponse
)
@require_access_token
@require_permission("user.user")
async def get_order_by_order_id(request: Request, order_id: int):
    order = await OrderService.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return OrderResponse.model_validate(order)


@orders.delete("/{order_id}", status_code=204, summary="Удалить заказ")
@require_access_token
@require_permission("manager.manager")
async def delete_order(request: Request, order_id: int):
    result = await OrderService.delete(order_id)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    return


@orders.post(
    "/",
    summary="Создать новый заказ",
    status_code=201,
    response_model=OrderCreateResponse,
)
@require_access_token
@require_permission("user.user")
async def add_new_order(request: Request, payload: NewOrderPayload):
    items_data = [
        {
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price_at_moment": float(item.price_at_moment),
        }
        for item in payload.items
    ]

    new_order = await OrderService.add(
        user_id=payload.user_id, items=items_data, status_id=payload.status_id
    )
    await produce_kafka_message(
        value={
            "event": "ORDER_CREATED",
            "order_id": new_order.id,
            "price": new_order.total_price,
        }
    )
    return {
        "message": "Заказ успешно создан",
        "order_id": new_order.id,
        "total_price": new_order.total_price,
    }


@orders.put("/{order_id}", summary="Изменить заказ", status_code=201)
@require_access_token
@require_permission("manager.manager")
async def put_order(request: Request, order_id: int, payload: OrderUpdatePayload):
    updated_order = await OrderService.update(order_id, payload)
    if not updated_order:
        raise HTTPException(status_code=404, detail="Заказ не найден")
    await produce_kafka_message(
        value={"event": "ORDER_UPDATED", order_id: payload.model_dump_json()}
    )
    return {"message": f"Заказ {order_id} успешно обновлен"}
