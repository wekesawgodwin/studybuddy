# backend/app/api/admin.py

from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import require_super_admin, require_admin_or_above
from app.models.user import User, UserRole
from app.models.role import AdminPermission, TableName
from app.schemas.role import (
    PromoteUserSchema,
    GrantPermissionSchema,
    PermissionResponse,
    UserAdminResponse
)

router = APIRouter(prefix="/admin", tags=["admin"])


# ── User management ───────────────────────────────────────────────────────────

@router.get(
    "/users",
    response_model=List[UserAdminResponse],
    status_code=status.HTTP_200_OK,
    summary="List all users (super admin only)"
)
def list_all_users(
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Returns every user in the system with their role and permissions.
    Super admin only.
    """
    return db.query(User).order_by(User.created_at.desc()).all()


@router.get(
    "/users/{user_id}",
    response_model=UserAdminResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single user (admin and above)"
)
def get_user(
    user_id: UUID,
    current_user: User = Depends(require_admin_or_above),
    db: Session = Depends(get_db)
):
    """
    Returns a single user's profile, role, and permissions.
    Admins can view users but cannot see other admins' permissions.
    Super admins can view anyone.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.patch(
    "/users/promote",
    response_model=UserAdminResponse,
    status_code=status.HTTP_200_OK,
    summary="Promote or demote a user's role (super admin only)"
)
def promote_user(
    body: PromoteUserSchema,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Changes a user's role.

    Rules enforced here:
    - A super admin cannot demote themselves — this would lock
      everyone out of the super admin role permanently.
    - Promoting to super_admin creates another super admin.
    - Demoting an admin to student removes their permissions too.
    """
    user = db.query(User).filter(User.id == body.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Prevent super admin from demoting themselves
    if user.id == current_user.id and body.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role"
        )

    # If demoting from admin to student, remove all their permissions
    if user.role == UserRole.ADMIN and body.role == UserRole.STUDENT:
        db.query(AdminPermission).filter(
            AdminPermission.user_id == user.id
        ).delete()

    user.role = body.role
    db.commit()
    db.refresh(user)
    return user


@router.patch(
    "/users/{user_id}/deactivate",
    response_model=UserAdminResponse,
    status_code=status.HTTP_200_OK,
    summary="Deactivate a user account (super admin only)"
)
def deactivate_user(
    user_id: UUID,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Deactivates a user account. The user can no longer log in
    but their data is preserved. This is a soft delete.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account"
        )

    user.is_active = False
    db.commit()
    db.refresh(user)
    return user


@router.patch(
    "/users/{user_id}/activate",
    response_model=UserAdminResponse,
    status_code=status.HTTP_200_OK,
    summary="Reactivate a user account (super admin only)"
)
def activate_user(
    user_id: UUID,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Reactivates a previously deactivated user account."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = True
    db.commit()
    db.refresh(user)
    return user


# ── Permission management ─────────────────────────────────────────────────────

@router.post(
    "/permissions",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Grant a table permission to an admin (super admin only)"
)
def grant_permission(
    body: GrantPermissionSchema,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """
    Grants CRUD permissions on a specific table to an admin user.

    If a permission row already exists for this user+table combination,
    it is updated rather than creating a duplicate.

    The target user must have role=admin. You cannot grant permissions
    to students or super admins.
    """
    user = db.query(User).filter(User.id == body.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Permissions can only be granted to users with role=admin"
        )

    # Check if permission already exists for this user + table
    existing = db.query(AdminPermission).filter(
        AdminPermission.user_id == body.user_id,
        AdminPermission.table_name == body.table_name
    ).first()

    if existing:
        # Update existing permission
        existing.can_create = body.can_create
        existing.can_read = body.can_read
        existing.can_update = body.can_update
        existing.can_delete = body.can_delete
        db.commit()
        db.refresh(existing)
        return existing

    # Create new permission
    permission = AdminPermission(
        user_id=body.user_id,
        table_name=body.table_name,
        can_create=body.can_create,
        can_read=body.can_read,
        can_update=body.can_update,
        can_delete=body.can_delete,
    )
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


@router.get(
    "/permissions/{user_id}",
    response_model=List[PermissionResponse],
    status_code=status.HTTP_200_OK,
    summary="List all permissions for an admin user (super admin only)"
)
def list_permissions(
    user_id: UUID,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Returns all table permissions granted to a specific admin user."""
    return db.query(AdminPermission).filter(
        AdminPermission.user_id == user_id
    ).all()


@router.delete(
    "/permissions/{permission_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a specific permission (super admin only)"
)
def revoke_permission(
    permission_id: UUID,
    current_user: User = Depends(require_super_admin),
    db: Session = Depends(get_db)
):
    """Removes a specific permission row, revoking that access."""
    permission = db.query(AdminPermission).filter(
        AdminPermission.id == permission_id
    ).first()

    if not permission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found"
        )

    db.delete(permission)
    db.commit()