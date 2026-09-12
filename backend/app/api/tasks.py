from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.task import Task
from backend.app.models.task_completion import TaskCompletion
from backend.app.schemas.task import (
    TaskCompletionResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
):
    db_task = Task(
        title=task.title,
        description=task.description,
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db),
):
    return db.query(Task).all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found.",
        )

    return task


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found.",
        )

    update_data = task_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


@router.post(
    "/{task_id}/complete",
    response_model=TaskCompletionResponse,
)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found.",
        )

    completion = TaskCompletion(
        task_id=task_id,
        completion_date=date.today(),
    )

    db.add(completion)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Task already completed today.",
        )

    db.refresh(completion)

    return completion


@router.get(
    "/{task_id}/completions",
    response_model=list[TaskCompletionResponse],
)
def get_task_completions(
    task_id: int,
    db: Session = Depends(get_db),
):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found.",
        )

    return (
        db.query(TaskCompletion)
        .filter(TaskCompletion.task_id == task_id)
        .order_by(TaskCompletion.completion_date.desc())
        .all()
    )
