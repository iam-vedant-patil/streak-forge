from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    user_id: int
    title: str
    description: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_active: bool | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str | None
    category: str | None
    created_at: datetime
    is_active: bool


class TaskCompletionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    completion_date: date
    completed_at: datetime


class TaskStreakResponse(BaseModel):
    task_id: int
    current_streak: int
    longest_streak: int
