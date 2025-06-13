import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, ForeignKey, Table, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db import Base


roles_permissions = Table(
    "roles_permissions",
    Base.metadata,
    Column(
        "role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "permission_id",
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

    permissions = relationship(
        "Permission", secondary=roles_permissions, back_populates="roles"
    )


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

    roles = relationship(
        "Role", secondary=roles_permissions, back_populates="permissions"
    )


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    name = Column(String, nullable=False)
    role_id = Column(
        Integer, ForeignKey("roles.id", ondelete="SET NULL"), nullable=True
    )
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    role = relationship("Role", backref="users")
