
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


ALLOWED_TRANSITIONS = {
    "Todo": {"Todo", "In Progress"},
    "In Progress": {"In Progress", "Todo", "Done"},
    "Done": {"Done"},
}


def create_task(db: Session, task_data: TaskCreate) -> Task:
    task = Task(**task_data.model_dump())

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def get_task(db: Session, task_id: int) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )

    return task


def list_tasks(
    db: Session,
    page: int = 1,
    limit: int = 10,
    task_status: str | None = None,
    priority: str | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
) -> dict:
    query = db.query(Task)

    if task_status is not None:
        query = query.filter(Task.status == task_status)

    if priority is not None:
        query = query.filter(Task.priority == priority)

    total = query.with_entities(func.count(Task.id)).scalar() or 0

    sort_columns = {
        "created_at": Task.created_at,
        "due_date": Task.due_date,
    }

    if sort_by not in sort_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort_by must be 'created_at' or 'due_date'",
        )

    if order not in {"asc", "desc"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="order must be 'asc' or 'desc'",
        )

    sort_column = sort_columns[sort_by]

    if order == "desc":
        query = query.order_by(sort_column.desc().nullslast())
    else:
        query = query.order_by(sort_column.asc().nullslast())

    tasks = (
        query.offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    total_pages = (total + limit - 1) // limit if total else 0

    return {
        "items": tasks,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
    }


def update_task(
    db: Session,
    task_id: int,
    task_data: TaskUpdate,
) -> Task:
    task = get_task(db, task_id)

    updates = task_data.model_dump(exclude_unset=True)

    # Validate the requested status transition.
    new_status = updates.get("status")

    if new_status is not None:
        allowed = ALLOWED_TRANSITIONS.get(task.status, set())

        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot transition task status "
                    f"from '{task.status}' to '{new_status}'"
                ),
            )

    # Apply only the fields supplied by the client.
    for field, value in updates.items():
        setattr(task, field, value)

    task.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)

    db.commit()
    db.refresh(task)

    return task


def delete_task(db: Session, task_id: int) -> None:
    task = get_task(db, task_id)

    db.delete(task)
    db.commit()
