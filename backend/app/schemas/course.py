# backend/app/schemas/course.py

from uuid import UUID
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class TopicBase(BaseModel):
    title: str
    sort_order: int = 0
    mastery_required: bool = True
    passing_score: int = 80


class TopicCreate(TopicBase):
    pass


class TopicResponse(TopicBase):
    id: UUID
    submodule_id: UUID
    content: Optional[str] = None
    content_filename: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class TopicSummary(TopicBase):
    """
    Lightweight topic for learning path lists.
    Does not include the full content blob.
    has_content tells the frontend whether a file has been uploaded.
    """
    id: UUID
    submodule_id: UUID
    content_filename: Optional[str] = None
    has_content: bool = False
    created_at: datetime
    model_config = {"from_attributes": True}


class SubModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    sort_order: int = 0


class SubModuleCreate(SubModuleBase):
    pass


class SubModuleResponse(SubModuleBase):
    id: UUID
    module_id: UUID
    created_at: datetime
    topics: List[TopicSummary] = []
    model_config = {"from_attributes": True}


class ModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    sort_order: int = 0


class ModuleCreate(ModuleBase):
    pass


class ModuleResponse(ModuleBase):
    id: UUID
    course_id: UUID
    created_at: datetime
    submodules: List[SubModuleResponse] = []
    model_config = {"from_attributes": True}


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    sort_order: int = 0
    status: bool = True


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[bool] = None


class CourseListResponse(CourseBase):
    id: UUID
    created_at: datetime
    model_config = {"from_attributes": True}


class CourseDetailResponse(CourseBase):
    id: UUID
    created_at: datetime
    modules: List[ModuleResponse] = []
    model_config = {"from_attributes": True}