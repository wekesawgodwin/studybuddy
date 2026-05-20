# backend/app/api/courses.py

from uuid import UUID
from typing import List
from fastapi import (
    APIRouter, Depends, HTTPException,
    status, UploadFile, File
)
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user, check_table_permission
from app.models.course import Course, Module, SubModule, Topic
from app.models.user import User
from app.models.role import TableName
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseListResponse, CourseDetailResponse,
    ModuleCreate, ModuleResponse,
    SubModuleCreate, SubModuleResponse,
    TopicCreate, TopicResponse, TopicSummary
)

router = APIRouter(prefix="/courses", tags=["courses"])
topics_router = APIRouter(prefix="/topics", tags=["topics"])


# ── Courses ───────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[CourseListResponse])
def list_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(Course)
        .filter(Course.status == True)  # noqa: E712
        .order_by(Course.sort_order)
        .all()
    )


@router.get("/{course_id}", response_model=CourseDetailResponse)
def get_course(
    course_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the full hierarchy: course -> modules -> submodules -> topic summaries.
    Topic content blobs are NOT included here — fetch them via GET /topics/{id}.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    if not course.status:
        raise HTTPException(status_code=403, detail="Course not available")
    return course


@router.post("/", response_model=CourseDetailResponse, status_code=201)
def create_course(
    body: CourseCreate,
    current_user: User = Depends(check_table_permission(TableName.COURSES, "create")),
    db: Session = Depends(get_db)
):
    course = Course(**body.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.patch("/{course_id}", response_model=CourseDetailResponse)
def update_course(
    course_id: UUID,
    body: CourseUpdate,
    current_user: User = Depends(check_table_permission(TableName.COURSES, "update")),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=204)
def delete_course(
    course_id: UUID,
    current_user: User = Depends(check_table_permission(TableName.COURSES, "delete")),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()


# ── Modules ───────────────────────────────────────────────────────────────────

@router.post("/{course_id}/modules", response_model=ModuleResponse, status_code=201)
def create_module(
    course_id: UUID,
    body: ModuleCreate,
    current_user: User = Depends(check_table_permission(TableName.MODULES, "create")),
    db: Session = Depends(get_db)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    module = Module(course_id=course_id, **body.model_dump())
    db.add(module)
    db.commit()
    db.refresh(module)
    return module


@router.delete("/{course_id}/modules/{module_id}", status_code=204)
def delete_module(
    course_id: UUID,
    module_id: UUID,
    current_user: User = Depends(check_table_permission(TableName.MODULES, "delete")),
    db: Session = Depends(get_db)
):
    module = db.query(Module).filter(
        Module.id == module_id,
        Module.course_id == course_id
    ).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    db.delete(module)
    db.commit()


# ── SubModules ────────────────────────────────────────────────────────────────

@router.post(
    "/{course_id}/modules/{module_id}/submodules",
    response_model=SubModuleResponse,
    status_code=201
)
def create_submodule(
    course_id: UUID,
    module_id: UUID,
    body: SubModuleCreate,
    current_user: User = Depends(check_table_permission(TableName.MODULES, "create")),
    db: Session = Depends(get_db)
):
    module = db.query(Module).filter(
        Module.id == module_id,
        Module.course_id == course_id
    ).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found in this course")
    submodule = SubModule(module_id=module_id, **body.model_dump())
    db.add(submodule)
    db.commit()
    db.refresh(submodule)
    return submodule


@router.delete(
    "/{course_id}/modules/{module_id}/submodules/{submodule_id}",
    status_code=204
)
def delete_submodule(
    course_id: UUID,
    module_id: UUID,
    submodule_id: UUID,
    current_user: User = Depends(check_table_permission(TableName.MODULES, "delete")),
    db: Session = Depends(get_db)
):
    submodule = db.query(SubModule).filter(
        SubModule.id == submodule_id,
        SubModule.module_id == module_id
    ).first()
    if not submodule:
        raise HTTPException(status_code=404, detail="SubModule not found")
    db.delete(submodule)
    db.commit()


# ── Topics ────────────────────────────────────────────────────────────────────

@router.post(
    "/{course_id}/modules/{module_id}/submodules/{submodule_id}/topics",
    response_model=TopicResponse,
    status_code=201
)
def create_topic(
    course_id: UUID,
    module_id: UUID,
    submodule_id: UUID,
    body: TopicCreate,
    current_user: User = Depends(check_table_permission(TableName.TOPICS, "create")),
    db: Session = Depends(get_db)
):
    """
    Creates a topic. Upload the markdown file separately via
    POST /topics/{topic_id}/upload after creating the topic.
    """
    submodule = db.query(SubModule).filter(
        SubModule.id == submodule_id,
        SubModule.module_id == module_id
    ).first()
    if not submodule:
        raise HTTPException(status_code=404, detail="SubModule not found")
    topic = Topic(submodule_id=submodule_id, **body.model_dump())
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


@router.delete(
    "/{course_id}/modules/{module_id}/submodules/{submodule_id}/topics/{topic_id}",
    status_code=204
)
def delete_topic(
    course_id: UUID,
    module_id: UUID,
    submodule_id: UUID,
    topic_id: UUID,
    current_user: User = Depends(check_table_permission(TableName.TOPICS, "delete")),
    db: Session = Depends(get_db)
):
    topic = db.query(Topic).filter(
        Topic.id == topic_id,
        Topic.submodule_id == submodule_id
    ).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    db.delete(topic)
    db.commit()


# ── Topic content (separate router at /topics) ────────────────────────────────

@topics_router.get("/{topic_id}", response_model=TopicResponse)
def get_topic(
    topic_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns a topic including its full markdown content blob."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@topics_router.post("/{topic_id}/upload", response_model=TopicResponse)
async def upload_topic_content(
    topic_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(check_table_permission(TableName.TOPICS, "update")),
    db: Session = Depends(get_db)
):
    """
    Uploads a .md, .markdown, or .txt file and stores its text content
    in the topic's content column. Replaces any existing content.

    Max file size: 5MB.
    Encoding: UTF-8 only.
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Validate file type
    filename = file.filename or ""
    ext = ("." + filename.rsplit(".", 1)[-1].lower()) if "." in filename else ""
    if ext not in {".md", ".markdown", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext}'. Accepted: .md, .markdown, .txt"
        )

    # Read and validate size
    content_bytes = await file.read()
    if len(content_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 5MB.")

    # Decode as UTF-8
    try:
        content_text = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded.")

    topic.content = content_text
    topic.content_filename = filename
    db.commit()
    db.refresh(topic)
    return topic


@topics_router.delete("/{topic_id}/content", response_model=TopicResponse)
def clear_topic_content(
    topic_id: UUID,
    current_user: User = Depends(check_table_permission(TableName.TOPICS, "update")),
    db: Session = Depends(get_db)
):
    """Removes the markdown content from a topic without deleting the topic."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    topic.content = None
    topic.content_filename = None
    db.commit()
    db.refresh(topic)
    return topic