"""Shared test fixtures.

Every test runs against an isolated in-memory SQLite database. The ``get_session``
dependency is overridden so the real ``cv.db`` is never opened during tests.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from main import app, get_session


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    # No context manager: the startup event calls create_all on the real
    # engine, which would open cv.db. Tests set up their own schema above.
    yield TestClient(app)
    app.dependency_overrides.clear()


def register_user(client, **overrides):
    """POST /register for a default valid user (any field overridable via kwargs).

    /register logs the new user in, so the client's session cookie is
    already set for that User afterwards. Returns the data posted, e.g. so a
    caller can log back in later with the same login_email/password.
    """
    data = {
        "login_email": "alice@example.com",
        "password": "hunter2hunter2",
        "username": "alice-dev",
        **overrides,
    }
    client.post("/register", data=data)
    return data
