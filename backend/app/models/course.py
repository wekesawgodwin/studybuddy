# backend/app/models/course.py

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, Integer,
    DateTime, ForeignKey, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Boolean, default=True, nullable=False, server_default="true")
    sort_order = Column(Integer, nullable=False, default=0, server_default="0")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    modules = relationship(
        "Module",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Module.sort_order"
    )


class Module(Base):
    __tablename__ = "modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(
        UUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0, server_default="0")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    course = relationship("Course", back_populates="modules")
    submodules = relationship(
        "SubModule",
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="SubModule.sort_order"
    )


class SubModule(Base):
    """
    A module subdivision that groups related topics.

    Example hierarchy:
      Course:    "Python Programming"
      Module:    "Core Concepts"
      SubModule: "Data Structures"
      Topic:     "Lists and Tuples"
    """
    __tablename__ = "submodules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = Column(
        UUID(as_uuid=True),
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False
    )
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0, server_default="0")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    module = relationship("Module", back_populates="submodules")
    topics = relationship(
        "Topic",
        back_populates="submodule",
        cascade="all, delete-orphan",
        order_by="Topic.sort_order"
    )


class Topic(Base):
    """
    The atomic learning unit.

    content stores the raw markdown file text uploaded by an admin.
    It is nullable because an admin may create the topic before
    uploading the content file.

    content_filename stores the original filename for display purposes.
    """
    __tablename__ = "topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submodule_id = Column(
        UUID(as_uuid=True),
        ForeignKey("submodules.id", ondelete="CASCADE"),
        nullable=False
    )
    title = Column(String(255), nullable=False)
    sort_order = Column(Integer, nullable=False, default=0, server_default="0")

    # Markdown file content stored as TEXT
    content = Column(Text, nullable=True)
    content_filename = Column(String(255), nullable=True)

    # Mastery gate
    mastery_required = Column(Boolean, default=True, nullable=False, server_default="true")
    passing_score = Column(Integer, default=80, nullable=False, server_default="80")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    submodule = relationship("SubModule", back_populates="topics")