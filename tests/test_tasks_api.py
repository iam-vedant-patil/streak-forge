from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.database import Base, get_db
from backend.app.main import app
from backend.app.models.task import Task
from backend.app.models.task_completion import TaskCompletion
from backend.app.models.user import User


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
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    user = User(
        username="testuser",
        email="test@example.com",
    )

    db.add(user)
    db.commit()
    db.close()

def teardown_database():
    Base.metadata.drop_all(bind=test_engine)


def test_get_task_streak():
    setup_database()

    db = TestingSessionLocal()

    task = Task(
        user_id=1,
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

    response = client.get(
        f"/tasks/{task_id}/streak",
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "task_id": task.id,
        "current_streak": 3,
        "longest_streak": 3,
    }

    teardown_database()


def test_get_task_streak_task_not_found():
    setup_database()

    response = client.get(
        "/tasks/999/streak",
        headers={"X-User-ID": "1"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found."
    }

    teardown_database()
def test_complete_task():
    setup_database()

    db = TestingSessionLocal()

    task = Task(
        user_id=1,
        title="Complete Me",
        description="Test completion",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    db.close()

    response = client.post(
        f"/tasks/{task_id}/complete",
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["task_id"] == task_id
    assert data["completion_date"] == date.today().isoformat()

    teardown_database()
def test_complete_task_rejects_other_users_task():
    setup_database()

    db = TestingSessionLocal()

    task = Task(
        user_id=2,
        title="User Two Task",
        description="Should not be completable by user one",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    db.close()

    response = client.post(
        f"/tasks/{task_id}/complete",
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found."
    }

    teardown_database()
def test_complete_task_twice_same_day():
    setup_database()

    db = TestingSessionLocal()

    task = Task(
        user_id=1,
        title="Complete Twice",
        description="Test duplicate completion",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    db.close()

    first_response = client.post(
        f"/tasks/{task_id}/complete",
        headers={"X-User-ID": "1"},
    )

    assert first_response.status_code == 200

    second_response = client.post(
        f"/tasks/{task_id}/complete",
        headers={"X-User-ID": "1"},
    )

    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Task already completed today."
    }

    teardown_database()
def test_complete_task_not_found():
    setup_database()

    response = client.post(
        "/tasks/999/complete",
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found."
    }

    teardown_database()
def test_get_task_completions():
    setup_database()

    db = TestingSessionLocal()

    task = Task(
        user_id=1,
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

    response = client.get(
        f"/tasks/{task_id}/completions",
        headers={"X-User-ID": "1"},
    )

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
        user_id=1,
        title="No History",
        description="Task with no completions",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    db.close()

    response = client.get(
        f"/tasks/{task_id}/completions",
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 200
    assert response.json() == []

    teardown_database()
def test_get_task_completions_task_not_found():
    setup_database()

    response = client.get(
        "/tasks/999/completions",
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found."
    }

    teardown_database()
def test_create_task():
    setup_database()

    response = client.post(
        "/tasks/",
        json={
            "user_id": 1,
            "title": "New API Task",
            "description": "Created through the API",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "New API Task"
    assert data["description"] == "Created through the API"
    assert "id" in data
    assert data["is_active"] is True

    teardown_database()
def test_create_task_assigns_category():
    setup_database()

    response = client.post(
        "/tasks/",
        json={
            "user_id": 1,
            "title": "Build Python API",
            "description": "Work on the FastAPI backend",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == "Programming"

    teardown_database()

def test_get_tasks_returns_only_current_users_tasks():
    setup_database()

    db = TestingSessionLocal()

    tasks = [
        Task(user_id=1, title="User One Task", description="First task"),
        Task(user_id=2, title="User Two Task", description="Second task"),
    ]

    db.add_all(tasks)
    db.commit()
    db.close()

    response = client.get(
        "/tasks/",
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["title"] == "User One Task"
    assert data[0]["user_id"] == 1

    teardown_database()

def test_get_task():
    setup_database()

    db = TestingSessionLocal()

    task = Task(
        user_id=1,
        title="Single Task",
        description="Get one task",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    db.close()

    response = client.get(
        f"/tasks/{task_id}",
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "Single Task"
    assert data["description"] == "Get one task"

    teardown_database()

def test_get_task_not_found():
    setup_database()

    response = client.get(
        "/tasks/999",
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found."
    }

    teardown_database()


def test_update_task():
    setup_database()

    db = TestingSessionLocal()

    task = Task(
        user_id=1,
        title="Old Title",
        description="Old description",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    db.close()

    response = client.patch(
        f"/tasks/{task_id}",
        headers={"X-User-ID": "1"},
        json={
            "title": "Updated Title",
            "description": "Updated description",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == task_id
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"

    teardown_database()


def test_update_task_partial():
    setup_database()

    db = TestingSessionLocal()

    task = Task(
        user_id=1,
        title="Original Title",
        description="Original description",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    db.close()

    response = client.patch(
        f"/tasks/{task_id}",
        headers={"X-User-ID": "1"},
        json={
            "title": "New Title",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "New Title"
    assert data["description"] == "Original description"

    teardown_database()


def test_update_task_not_found():
    setup_database()

    response = client.patch(
        "/tasks/999",
        headers={"X-User-ID": "1"},
        json={
            "title": "Updated Title",
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found."
    }

    teardown_database()

def test_user_cannot_access_another_users_task():
    setup_database()

    db = TestingSessionLocal()

    second_user = User(
        username="seconduser",
        email="second@example.com",
    )

    db.add(second_user)
    db.commit()
    db.refresh(second_user)

    task = Task(
        user_id=second_user.id,
        title="Private Task",
        description="Belongs to user 2",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    db.close()

    response = client.get(
        f"/tasks/{task_id}",
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found."
    }

    teardown_database()

def test_user_cannot_access_another_users_task_completions():
    setup_database()

    db = TestingSessionLocal()

    second_user = User(
        username="seconduser",
        email="second@example.com",
    )

    db.add(second_user)
    db.commit()
    db.refresh(second_user)

    task = Task(
        user_id=second_user.id,
        title="Private Task",
        description="Belongs to user 2",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    db.close()

    response = client.get(
        f"/tasks/{task_id}/completions",
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found."
    }

    teardown_database()
def test_user_cannot_access_another_users_task_streak():
    setup_database()

    db = TestingSessionLocal()

    second_user = User(
        username="seconduser",
        email="second@example.com",
    )

    db.add(second_user)
    db.commit()
    db.refresh(second_user)

    task = Task(
        user_id=second_user.id,
        title="Private Task",
        description="Belongs to user 2",
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    task_id = task.id

    db.close()

    response = client.get(
        f"/tasks/{task_id}/streak",
        headers={"X-User-ID": "1"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Task not found."
    }

    teardown_database()
