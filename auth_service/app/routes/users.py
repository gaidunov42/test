from fastapi import APIRouter, HTTPException, Request

from app.schemas.schemas import UserUpdateRequest, UserResponse
from app.crud.users import UserCrud
from app.services.check_token_service import require_access_token, require_permission


users = APIRouter(prefix="/users", tags=["Работа с пользователями"])


@users.put(
    "/put_user",
    summary="Редактировать пользователя",
    status_code=201,
    response_model=UserResponse,
)
@require_access_token
@require_permission("manager.manager")
async def put_user(request: Request):
    data = await request.json()
    user_data = UserUpdateRequest(**data)

    try:
        user = await UserCrud.update_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.name if user.role else None,
    )
