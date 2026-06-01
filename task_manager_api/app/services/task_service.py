from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, PaginatedTasks
from app.config.settings import settings


def create_task(payload: TaskCreate, current_user: User, db: Session) -> TaskResponse:
    task = Task(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        status=payload.status,
        user_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskResponse.model_validate(task)


def get_tasks(
    current_user: User,
    db: Session,
    status_filter: TaskStatus | None,
    priority_filter: TaskPriority | None,
    search: str | None,
    page: int,
    page_size: int,
) -> PaginatedTasks:
    page_size = min(page_size, settings.MAX_PAGE_SIZE)
    query = db.query(Task).filter(Task.user_id == current_user.id)

    if status_filter:
        query = query.filter(Task.status == status_filter)
    if priority_filter:
        query = query.filter(Task.priority == priority_filter)
    if search:
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(Task.title.ilike(term), Task.description.ilike(term))
        )

    total = query.count()
    tasks = query.order_by(Task.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedTasks(
        total=total,
        page=page,
        page_size=page_size,
        results=[TaskResponse.model_validate(t) for t in tasks],
    )


def get_task_by_id(task_id: int, current_user: User, db: Session) -> TaskResponse:
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return TaskResponse.model_validate(task)


def update_task(task_id: int, payload: TaskUpdate, current_user: User, db: Session) -> TaskResponse:
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # only update fields the caller actually sent
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return TaskResponse.model_validate(task)


def delete_task(task_id: int, current_user: User, db: Session) -> dict:
    task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": f"Task '{task.title}' deleted successfully"}
