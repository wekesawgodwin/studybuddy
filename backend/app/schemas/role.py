# backend/app/schemas/role.py

from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.models.user import UserRole
from app.models.role import TableName


class PromoteUserSchema(BaseModel):
    """
    Request body for promoting a user to admin or super_admin.
    Only a super admin can call the endpoint that uses this schema.
    """
    user_id: UUID
    role: UserRole


class GrantPermissionSchema(BaseModel):
    """
    Request body for granting a specific table permission to an admin.
    Super admin only.
    """
    user_id: UUID
    table_name: TableName
    can_create: bool = False
    can_read: bool = False
    can_update: bool = False
    can_delete: bool = False


class PermissionResponse(BaseModel):
    """Response shape for a single admin permission row."""
    id: UUID
    user_id: UUID
    table_name: TableName
    can_create: bool
    can_read: bool
    can_update: bool
    can_delete: bool
    granted_at: datetime

    model_config = {"from_attributes": True}


class UserAdminResponse(BaseModel):
    """
    Response shape for user management endpoints.
    Includes role and permissions.
    """
    id: UUID
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    permissions: list[PermissionResponse] = []

    model_config = {"from_attributes": True}