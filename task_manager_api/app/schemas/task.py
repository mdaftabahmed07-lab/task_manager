from datetime import datetime
from pydantic import BaseModel, field_validator
from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: TaskPriority = TaskPriority.medium
    status: TaskStatus = TaskStatus.todo

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Task title cannot be blank")
        return v


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str | None) -> str | None:
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Task title cannot be blank")
        return v


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    priority: TaskPriority
    status: TaskStatus
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedTasks(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[TaskResponse]
