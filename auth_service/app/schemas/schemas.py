from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

from typing import Optional, List


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=100)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    user_agent: str
    ip_address: str


class LoginResponse(BaseModel):
    message: str


class PermissionSchema(BaseModel):
    code: str
    description: str

    class Config:
        orm_mode = True


class RoleWithPermissionsSchema(BaseModel):
    name: str
    description: str
    permissions: List[PermissionSchema]

    class Config:
        orm_mode = True


class RoleCreateRequest(BaseModel):
    name: str
    description: str
    permissions: List[str]


class UserUpdateRequest(BaseModel):
    id: UUID
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role_id: Optional[int] = None


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    role: Optional[str]

    class Config:
        orm_mode = True
