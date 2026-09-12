from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models.task import Task
from backend.app.models.task_completion import TaskCompletion


# Create a separate in-memory database for API tests.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def setup_database():
    Base.metadata.create_all(bind=test_engine)


def teardown_database():
    Base.metadata.drop_all(bind=test_engine)


def test_get_task_streak():
    setup_database()

    db = TestingSessionLocal()

    task = Task(
        title="Test Task",
        description="API test task",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    today = date.today()

    completions = [
        TaskCompletion(
            task_id=task.id,
            completion_date=today,
        ),
        TaskCompletion(
            task_id=task.id,
            completion_date=today - timedelta(days=1),
        ),
        TaskCompletion(
            task_id=task.id,
            completion_date=today - timedelta(days=2),
        ),
        TaskCompletion(
            task_id=task.id,
            completion_date=today - timedelta(days=5),
        ),
    ]

    db.add_all(completions)
    db.commit()

    task_id = task.id

    db.close()

    response = client.get(f"/tasks/{task_id}/streak")
    assert response.status_code == 200
    assert response.json() == {
        "task_id": task.id,
        "current_streak": 3,
        "longest_streak": 3,
    }

    teardown_database()
