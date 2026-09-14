from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.auth import get_current_user
from backend.app.database import Base
from backend.app.models.user import User


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

    return db


def test_get_current_user_returns_user():
    db = setup_database()

    user = get_current_user(
        x_user_id=1,
        db=db,
    )

    assert user.id == 1
    assert user.username == "testuser"

    db.close()

def test_get_current_user_requires_user_id():
    db = setup_database()

    try:
        get_current_user(
            x_user_id=None,
            db=db,
        )
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 401
        assert exc.detail == "Authentication required."

    db.close()


def test_get_current_user_rejects_invalid_user_id():
    db = setup_database()

    try:
        get_current_user(
            x_user_id=999,
            db=db,
        )
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 401
        assert exc.detail == "Invalid user."

    db.close()
