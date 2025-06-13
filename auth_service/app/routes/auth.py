from fastapi import APIRouter, HTTPException, Response, Request
from loguru import logger

from app.schemas.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    LoginResponse,
    UserResponse,
)
from app.crud.auth import UserCrud
from app.services.token_service import jwt_service


auth = APIRouter(prefix="/auth", tags=["Авторицация/Аутентификация"])


@auth.post("/register", summary="Регистрация нового пользователя")
async def register_user(user: UserRegisterRequest):
    try:
        await UserCrud.create(
            email=user.email, full_name=user.full_name, password=user.password
        )
        return {"detail": "User registered successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail="Ошибка сервера при регистрации")


@auth.post(
    "/login",
    summary="Вход, получение JWT",
    status_code=200,
    response_model=LoginResponse,
)
async def authentication(payload: UserLoginRequest, response: Response):
    try:
        user = await UserCrud.authenticate(
            email=payload.email, password=payload.password
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    permissions = [perm.code for perm in user.role.permissions]
    access_token = jwt_service.create_access_token(str(user.id), permissions)
    refresh_token = await jwt_service.create_refresh_token(
        str(user.id), permissions, {"ua": payload.user_agent, "ip": payload.ip_address}
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=int(jwt_service.access_token_ttl.total_seconds()),
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=int(jwt_service.refresh_token_ttl.total_seconds()),
    )
    return {"message": "Успешный вход"}


@auth.get(
    "/me", summary="Получить информацию о пользователе", response_model=UserResponse
)
async def get_user_info(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Access token отсутствует")

    try:
        user_id = jwt_service.get_user_id_from_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Недействительный access token")
    user = await UserCrud.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.name if user.role else "unknown",
    )


@auth.get("/refresh", summary="Обновление JWT", status_code=201)
async def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Отсутствует refresh_token")
    try:
        access_token, new_refresh_token = await jwt_service.rotate_tokens(
            refresh_token=refresh_token,
            metadata={
                "ip": request.client.host,
                "ua": request.headers.get("user-agent", ""),
            },
        )
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=401, detail="Недействительный или отозванный refresh_token"
        )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=int(jwt_service.access_token_ttl.total_seconds()),
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=int(jwt_service.refresh_token_ttl.total_seconds()),
    )

    return {"message": "Токены обновлены"}


@auth.get("/logout", summary="Выйти с текущего устройства", status_code=201)
async def logout(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Нет refresh_token")

    try:
        payload = await jwt_service.verify_refresh_token(refresh_token)
        user_id = payload["user_id"]
        token_id = payload["jti"]
        await jwt_service.redis_store.delete_token(user_id, token_id)
    except Exception:
        logger.error(f"Ошибка проверки токена пользователя: {refresh_token}")
        pass  # дроп кук даже если ошибка
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Вы вышли из системы на этом устройстве"}


@auth.get("/logout_all", summary="Выйти со всех устройств", status_code=200)
async def logout_all(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Нет refresh_token")
    try:
        payload = await jwt_service.verify_refresh_token(refresh_token)
        user_id = payload["user_id"]
        await jwt_service.redis_store.delete_all_tokens_for_user(user_id)
    except Exception:
        logger.error(f"Ошибка проверки токена пользователя: {refresh_token}")
        pass
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Вы вышли из системы на всех устройствах"}
