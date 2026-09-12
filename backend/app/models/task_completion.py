from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

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

    completion_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    completed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
