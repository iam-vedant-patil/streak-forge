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


def test_get_task_streak_task_not_found():
    setup_database()

    response = client.get("/tasks/999/streak")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found."
    }

    teardown_database()
def test_complete_task():
    setup_database()

    db = TestingSessionLocal()

    task = Task(
        title="Complete Me",
        description="Test completion",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    db.close()

    response = client.post(f"/tasks/{task_id}/complete")

    assert response.status_code == 200

    data = response.json()

    assert data["task_id"] == task_id
    assert data["completion_date"] == date.today().isoformat()

    teardown_database()
def test_complete_task_twice_same_day():
    setup_database()

    db = TestingSessionLocal()

    task = Task(
        title="Complete Twice",
        description="Test duplicate completion",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    db.close()

    first_response = client.post(f"/tasks/{task_id}/complete")

    assert first_response.status_code == 200

    second_response = client.post(f"/tasks/{task_id}/complete")

    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Task already completed today."
    }

    teardown_database()
def test_complete_task_not_found():
    setup_database()

    response = client.post("/tasks/999/complete")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found."
    }

    teardown_database()
def test_get_task_completions():
    setup_database()

    db = TestingSessionLocal()

    task = Task(
        title="History Test",
        description="Test completion history",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id
    today = date.today()

    completions = [
        TaskCompletion(
            task_id=task_id,
            completion_date=today,
        ),
        TaskCompletion(
            task_id=task_id,
            completion_date=today - timedelta(days=1),
        ),
        TaskCompletion(
            task_id=task_id,
            completion_date=today - timedelta(days=3),
        ),
    ]

    db.add_all(completions)
    db.commit()
    db.close()

    response = client.get(f"/tasks/{task_id}/completions")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3

    assert data[0]["completion_date"] == today.isoformat()
    assert data[1]["completion_date"] == (
        today - timedelta(days=1)
    ).isoformat()
    assert data[2]["completion_date"] == (
        today - timedelta(days=3)
    ).isoformat()

    teardown_database()
def test_get_task_completions_empty():
    setup_database()

    db = TestingSessionLocal()

    task = Task(
        title="No History",
        description="Task with no completions",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    db.close()

    response = client.get(f"/tasks/{task_id}/completions")

    assert response.status_code == 200
    assert response.json() == []

    teardown_database()
def test_get_task_completions_task_not_found():
    setup_database()

    response = client.get("/tasks/999/completions")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found."
    }

    teardown_database()
