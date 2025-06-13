from typing import List
from fastapi import APIRouter, HTTPException, Request, status

from app.schemas.schemas import (
    RoleWithPermissionsSchema,
    RoleCreateRequest,
    PermissionSchema,
)
from app.crud.roles import RolesCrud
from app.services.check_token_service import require_access_token, require_permission


roles = APIRouter(prefix="/roles", tags=["Работа с ролями и разрешениями"])


@roles.get(
    "/all",
    summary="Получить все роли, разрешения и отношения",
    response_model=List[RoleWithPermissionsSchema],
)
@require_access_token
@require_permission("manager.manager")
async def get_user_info(request: Request):
    return await RolesCrud.roles_with_permissions()


@roles.post(
    "/add_role",
    summary="Добавить новую роль, установить разрешения",
    status_code=201,
    response_model=RoleWithPermissionsSchema,
)
@require_access_token
@require_permission("manager.manager")
async def add_role(request: Request):
    data = await request.json()
    role_data = RoleCreateRequest(**data)
    existing_role = await RolesCrud.get_role_by_name(role_data.name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Роль с таким именем уже существует.",
        )
    new_role = await RolesCrud.create_role(
        name=role_data.name,
        description=role_data.description,
        permission_codes=role_data.permissions,
    )
    return new_role


@roles.post(
    "/add_permission",
    summary="Добавить разрешение",
    status_code=201,
    response_model=PermissionSchema,
)
@require_access_token
@require_permission("manager.manager")
async def add_role(request: Request):
    data = await request.json()
    permission_data = PermissionSchema(**data)

    existing = await RolesCrud.get_by_code(permission_data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Разрешение с таким кодом уже существует",
        )

    new_permission = await RolesCrud.create(
        code=permission_data.code, description=permission_data.description
    )

    return new_permission
