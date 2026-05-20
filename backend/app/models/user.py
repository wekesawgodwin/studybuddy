import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class UserRole(str, enum.Enum):
    """
    Inheriting from str means the enum value is used directly
    when the object is converted to a string.
    e.g. str(UserRole.SUPER_ADMIN) == "super_admin"
    """
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    STUDENT = "student"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auth_provider = Column(String(50), nullable=False, default="email_otp")
    auth_subject_id = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)

    # values_callable tells SQLAlchemy to use the .value of each enum
    # member ("super_admin") instead of the .name ("SUPER_ADMIN").
    # Without this SQLAlchemy sends the uppercase name to PostgreSQL
    # which does not match the lowercase enum type in the database.
    role = Column(
        SQLEnum(
            UserRole,
            name="user_role",
            values_callable=lambda x: [e.value for e in x]
        ),
        nullable=False,
        default=UserRole.STUDENT
    )

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    permissions = relationship(
        "AdminPermission",
        back_populates="user",
        cascade="all, delete-orphan"
    )