"""Tests for GET/POST /register: account creation, username rules, session login."""

from sqlmodel import Session, select

from main import User


VALID = {
    "login_email": "alice@example.com",
    "password": "hunter2hunter2",
    "username": "alice-dev",
}


def test_register_page_renders(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b'name="login_email"' in response.content
    assert b'name="password"' in response.content
    assert b'name="username"' in response.content


def test_register_success_creates_user_logs_in_and_redirects(client, session: Session):
    response = client.post("/register", data=VALID)
    assert response.status_code == 200  # redirect to /form is followed

    users = session.exec(select(User)).all()
    assert len(users) == 1
    assert users[0].username == "alice-dev"
    assert users[0].login_email == "alice@example.com"

    # A session cookie was set (the new user is logged in).
    assert "session" in client.cookies


def test_register_password_is_hashed(client, session: Session):
    client.post("/register", data=VALID)

    user = session.exec(select(User)).one()
    assert user.hashed_password != VALID["password"]
    assert user.hashed_password.startswith("$2b$")


def test_register_rejects_username_bad_characters(client, session: Session):
    response = client.post(
        "/register", data={**VALID, "username": "Alice_Dev!"}
    )
    assert response.status_code == 200
    assert session.exec(select(User)).all() == []


def test_register_rejects_username_too_short(client, session: Session):
    response = client.post("/register", data={**VALID, "username": "ab"})
    assert response.status_code == 200
    assert session.exec(select(User)).all() == []


def test_register_rejects_reserved_username(client, session: Session):
    response = client.post("/register", data={**VALID, "username": "form"})
    assert response.status_code == 200
    assert session.exec(select(User)).all() == []


def test_register_rejects_username_colliding_with_entity_route(
    client, session: Session
):
    # "/skills" is already an existing top-level route; a Username here would
    # collide with it once portfolios are served at "/<username>".
    response = client.post("/register", data={**VALID, "username": "skills"})
    assert response.status_code == 200
    assert session.exec(select(User)).all() == []


def test_register_rejects_taken_username(client, session: Session):
    client.post("/register", data=VALID)
    response = client.post(
        "/register",
        data={**VALID, "login_email": "someoneelse@example.com"},
    )
    assert response.status_code == 200
    assert len(session.exec(select(User)).all()) == 1


def test_register_rejects_duplicate_login_email(client, session: Session):
    client.post("/register", data=VALID)
    response = client.post(
        "/register", data={**VALID, "username": "someone-else"}
    )
    assert response.status_code == 200
    assert len(session.exec(select(User)).all()) == 1
