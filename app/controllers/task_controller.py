
from sqlalchemy.orm import Session

from app.schemas.task import TaskCreate, TaskUpdate
from app.services import task_service


def create_task(db: Session, task_data: TaskCreate):
    return task_service.create_task(db, task_data)


def get_task(db: Session, task_id: int):
    return task_service.get_task(db, task_id)


def list_tasks(
    db: Session,
    page: int = 1,
    limit: int = 10,
    task_status: str | None = None,
    priority: str | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
):
    return task_service.list_tasks(
        db=db,
        page=page,
        limit=limit,
        task_status=task_status,
        priority=priority,
        sort_by=sort_by,
        order=order,
    )


def update_task(
    db: Session,
    task_id: int,
    task_data: TaskUpdate,
):
    return task_service.update_task(db, task_id, task_data)


def delete_task(db: Session, task_id: int):
    task_service.delete_task(db, task_id)
