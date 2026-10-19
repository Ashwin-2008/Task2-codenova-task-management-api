
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.controllers import task_controller
from app.database import get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])

DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_data: TaskCreate,
    db: DatabaseSession,
):
    return task_controller.create_task(db, task_data)


@router.get("")
def list_tasks(
    db: DatabaseSession,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    task_status: Literal["Todo", "In Progress", "Done"] | None = Query(
        default=None,
        alias="status",
    ),
    priority: Literal["Low", "Medium", "High"] | None = None,
    sort_by: Literal["created_at", "due_date"] = "created_at",
    order: Literal["asc", "desc"] = "desc",
):
    result = task_controller.list_tasks(
        db=db,
        page=page,
        limit=limit,
        task_status=task_status,
        priority=priority,
        sort_by=sort_by,
        order=order,
    )

    return {
        **result,
        "items": [
            TaskResponse.model_validate(task)
            for task in result["items"]
        ],
    }


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: DatabaseSession):
    return task_controller.get_task(db, task_id)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: DatabaseSession,
):
    return task_controller.update_task(db, task_id, task_data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: DatabaseSession):
    task_controller.delete_task(db, task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
