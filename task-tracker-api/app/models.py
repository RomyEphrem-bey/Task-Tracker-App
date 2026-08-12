from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from pydantic import BaseModel, Field, ConfigDict, field_validator

class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


def validate_tags(tags: list[str]) -> list[str]:
    """Strip whitespace from each tag and remove duplicates.

    Args:
        tags (list[str]): The raw tag values to validate.

    Returns:
        list[str]: The cleaned tags, deduplicated while preserving
            their original order.

    Raises:
        ValueError: If any tag is blank after stripping whitespace.
    """
    cleaned_tags: list[str] = []

    for tag in tags:
        cleaned_tag = tag.strip()

        if not cleaned_tag:
            raise ValueError("Tags cannot be blank")

        if len(cleaned_tag) > 50:
            raise ValueError("Tags must be 50 characters or fewer")

        if cleaned_tag not in cleaned_tags:
            cleaned_tags.append(cleaned_tag)

    if len(cleaned_tags) > 20:
        raise ValueError("A task can have at most 20 tags")

    return cleaned_tags


class TaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=False, extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    tags: list[str] = Field(default_factory=list)

    @field_validator("title")
    @classmethod
    def _title_not_blank(cls, v: str) -> str:
        v2 = v.strip()
        if not v2:
            raise ValueError("Title is required and cannot be blank")
        if len(v2) > 200:
            raise ValueError("Title must be 200 characters or fewer")
        return v2

    @field_validator("description")
    @classmethod
    def _description_max_length(cls, v):
        if v is not None and len(v) > 2000:
            raise ValueError("Description must be 2000 characters or fewer")
        return v

    @field_validator("assignee")
    @classmethod
    def _assignee_max_length(cls, v):
        if v is not None and len(v) > 100:
            raise ValueError("Assignee must be 100 characters or fewer")
        return v

    @field_validator("tags")
    @classmethod
    def _validate_tags(cls, tags: list[str]) -> list[str]:
        return validate_tags(tags)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    tags: Optional[list[str]] = None

    @field_validator("title")
    @classmethod
    def _title_not_blank(cls, v):
        if v is None:
            return v
        v2 = v.strip()
        if not v2:
            raise ValueError("Title is required and cannot be blank")
        if len(v2) > 200:
            raise ValueError("Title must be 200 characters or fewer")
        return v2

    @field_validator("description")
    @classmethod
    def _description_max_length(cls, v):
        if v is not None and len(v) > 2000:
            raise ValueError("Description must be 2000 characters or fewer")
        return v

    @field_validator("assignee")
    @classmethod
    def _assignee_max_length(cls, v):
        if v is not None and len(v) > 100:
            raise ValueError("Assignee must be 100 characters or fewer")
        return v

    @field_validator("tags")
    @classmethod
    def _validate_tags(cls, tags: Optional[list[str]]) -> Optional[list[str]]:
        if tags is None:
            return None

        return validate_tags(tags)


class Comment(BaseModel):
    id: str
    text: str
    created_at: datetime


class CommentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str

    @field_validator("text")
    @classmethod
    def _text_not_blank(cls, v: str) -> str:
        v2 = v.strip()
        if not v2:
            raise ValueError("Comment text is required and cannot be blank")
        if len(v2) > 1000:
            raise ValueError("Comment text must be 1000 characters or fewer")
        return v2


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    tags: list[str] = Field(default_factory=list)
    comments: list[Comment] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: str