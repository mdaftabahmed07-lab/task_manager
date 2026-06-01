from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.task import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, PaginatedTasks
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task for the authenticated user."""
    return task_service.create_task(payload, current_user, db)


@router.get("", response_model=PaginatedTasks)
def list_tasks(
    status: TaskStatus | None = Query(None, description="Filter by status"),
    priority: TaskPriority | None = Query(None, description="Filter by priority"),
    search: str | None = Query(None, description="Search in title or description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Results per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all tasks for the logged-in user.

    Supports filtering by `status` and `priority`, full-text `search`,
    and standard `page` / `page_size` pagination.
    """
    return task_service.get_tasks(current_user, db, status, priority, search, page, page_size)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a single task by ID (must belong to the authenticated user)."""
    return task_service.get_task_by_id(task_id, current_user, db)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a task.  Only the fields you send will be changed
    (partial update — you don't need to resend everything).
    """
    return task_service.update_task(task_id, payload, current_user, db)


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Permanently delete a task."""
    return task_service.delete_task(task_id, current_user, db)
