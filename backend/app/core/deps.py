# backend/app/core/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole
from app.models.role import AdminPermission, TableName

bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Validates the JWT and returns the current user.
    Raises 401 if the token is invalid or the user does not exist.
    Raises 403 if the user account is deactivated.
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is missing user ID"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    return user


def require_super_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that restricts access to super admins only.

    Usage:
        @router.delete("/users/{user_id}")
        def delete_user(current_user: User = Depends(require_super_admin)):
            ...
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return current_user


def require_admin_or_above(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that restricts access to admins and super admins.
    Students are blocked.

    Usage:
        @router.post("/courses/")
        def create_course(current_user: User = Depends(require_admin_or_above)):
            ...
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_student(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that allows only students.
    Used for endpoints that students own exclusively,
    like their own progress or test attempts.

    Usage:
        @router.post("/topics/{topic_id}/attempts")
        def submit_attempt(current_user: User = Depends(require_student)):
            ...
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is for students only"
        )
    return current_user


def check_table_permission(table: TableName, action: str):
    """
    Factory function that returns a dependency checking whether
    the current user has a specific CRUD permission on a table.

    action must be one of: "create", "read", "update", "delete"

    Super admins always pass — they have implicit full access.
    Admins pass only if they have an AdminPermission row granting
    the requested action on the requested table.
    Students always fail.

    Usage:
        @router.post("/courses/")
        def create_course(
            current_user: User = Depends(
                check_table_permission(TableName.COURSES, "create")
            )
        ):
            ...
    """
    def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:

        # Super admins have full access to everything — no check needed
        if current_user.role == UserRole.SUPER_ADMIN:
            return current_user

        # Students have no admin permissions — always deny
        if current_user.role == UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to {action} {table.value}"
            )

        # Admins — check their specific permission row for this table
        permission = db.query(AdminPermission).filter(
            AdminPermission.user_id == current_user.id,
            AdminPermission.table_name == table
        ).first()

        if not permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You have not been granted any access to {table.value}"
            )

        # Check the specific CRUD flag
        flag_map = {
            "create": permission.can_create,
            "read": permission.can_read,
            "update": permission.can_update,
            "delete": permission.can_delete,
        }

        if not flag_map.get(action, False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have {action} permission on {table.value}"
            )

        return current_user

    return dependency