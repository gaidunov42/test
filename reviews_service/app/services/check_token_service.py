from functools import wraps
from fastapi import Request, Response, HTTPException
from app.services.token_service import jwt_service


def require_access_token(handler):
    @wraps(handler)
    async def wrapper(request: Request, *args, **kwargs):
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Access token отсутствует")
        try:
            jwt_service.verify_access_token(token)
        except Exception:
            raise HTTPException(
                status_code=401, detail="Неверный или просроченный access token"
            )
        return await handler(request, *args, **kwargs)

    return wrapper


def require_permission(required_permission: str):
    def decorator(handler):
        @wraps(handler)
        async def wrapper(request: Request, *args, **kwargs):
            token = request.cookies.get("access_token")
            if not token:
                raise HTTPException(status_code=401, detail="Access token отсутствует")

            try:
                payload = jwt_service.verify_access_token(token)
                permissions = payload.get("permissions", [])
            except Exception:
                raise HTTPException(
                    status_code=401, detail="Неверный или просроченный access token"
                )

            if required_permission not in permissions:
                raise HTTPException(status_code=403, detail="Недостаточно прав")

            return await handler(request, *args, **kwargs)

        return wrapper

    return decorator
