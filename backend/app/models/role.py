# backend/app/models/role.py

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base
import enum


class TableName(str, enum.Enum):
    """
    Every table an admin can be granted permissions on.
    Add new table names here as new sprints add new tables.
    """
    COURSES = "courses"
    MODULES = "modules"
    TOPICS = "topics"
    USERS = "users"
    ENROLLMENTS = "enrollments"
    MARKDOWN_DOCUMENTS = "markdown_documents"
    LLM_GENERATION_JOBS = "llm_generation_jobs"
    MASTERY_TEST_ATTEMPTS = "mastery_test_attempts"
    LIVES_ACCOUNTS = "lives_accounts"
    GEM_ACCOUNTS = "gem_accounts"
    ANALYTICS = "analytics"


class AdminPermission(Base):
    """
    Stores per-table CRUD permissions for admin users.

    Each row represents one admin's access to one table.
    Super admins never have rows here — they have full access by role.

    Example rows:
      user_id=abc, table_name=courses, can_create=True, can_read=True,
      can_update=True, can_delete=False
      → This admin can manage courses but cannot delete them.
    """
    __tablename__ = "admin_permissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # The admin user this permission belongs to
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Which table this permission controls
    table_name = Column(
        SQLEnum(TableName, name="table_name"),
        nullable=False
    )

    # CRUD flags — each defaults to False (deny by default)
    can_create = Column(Boolean, default=False, nullable=False)
    can_read = Column(Boolean, default=False, nullable=False)
    can_update = Column(Boolean, default=False, nullable=False)
    can_delete = Column(Boolean, default=False, nullable=False)

    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship back to the user
    user = relationship("User", back_populates="permissions")