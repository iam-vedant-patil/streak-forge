from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class TaskCompletion(Base):
    __tablename__ = "task_completions"

    __table_args__ = (
        UniqueConstraint(
            "task_id",
            "completion_date",
            name="uq_task_completion_date",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id"),
        nullable=False,
    )
    task: Mapped["Task"] = relationship(
        back_populates="completions",
    )

    completion_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    completed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


if TYPE_CHECKING:
    from backend.app.models.task import Task
