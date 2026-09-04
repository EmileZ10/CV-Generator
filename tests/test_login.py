"""Tests for GET/POST /login, POST /logout, and the auth gate on / and /form."""

from sqlmodel import Session, select

from main import User, pwd_context


VALID = {
    "login_email": "alice@example.com",
    "password": "hunter2hunter2",
    "username": "alice-dev",
}


def register(client, **overrides):
    data = {**VALID, **overrides}
    client.post("/register", data=data)
    client.cookies.clear()  # registration logs the user in; start signed out


def test_login_page_renders(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b'name="login_email"' in response.content
    assert b'name="password"' in response.content


def test_login_success_sets_session_and_redirects_to_form(client, session: Session):
    register(client)

    response = client.post(
        "/login",
        data={"login_email": VALID["login_email"], "password": VALID["password"]},
    )
    assert response.status_code == 200  # redirect to /form is followed
    assert response.url.path == "/form"
    assert "session" in client.cookies


def test_login_wrong_password_rerenders_with_error_and_no_session(
    client, session: Session
):
    register(client)

    response = client.post(
        "/login",
        data={"login_email": VALID["login_email"], "password": "wrong-password"},
    )
    assert response.status_code == 200
    assert response.url.path == "/login"
    assert "session" not in client.cookies


def test_login_unknown_email_rerenders_with_error_and_no_session(
    client, session: Session
):
    response = client.post(
        "/login",
        data={"login_email": "nobody@example.com", "password": "whatever123"},
    )
    assert response.status_code == 200
    assert response.url.path == "/login"
    assert "session" not in client.cookies


def test_logout_clears_session(client, session: Session):
    register(client)
    client.post(
        "/login",
        data={"login_email": VALID["login_email"], "password": VALID["password"]},
    )
    assert "session" in client.cookies

    response = client.post("/logout")
    assert response.status_code == 200  # redirect to / is followed
    assert response.url.path == "/"

    # The cleared session no longer grants access to /form.
    form_response = client.get("/form")
    assert form_response.url.path == "/login"


def test_home_redirects_to_form_when_logged_in(client, session: Session):
    register(client)
    client.post(
        "/login",
        data={"login_email": VALID["login_email"], "password": VALID["password"]},
    )

    response = client.get("/")
    assert response.status_code == 200  # redirect to /form is followed
    assert response.url.path == "/form"


def test_home_renders_entry_point_when_anonymous(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.url.path == "/"
    # No portfolio content and no listing of other Users.
    assert b"pf-hero" not in response.content
    assert b'href="/login"' in response.content
    assert b'href="/register"' in response.content


def test_form_redirects_to_login_when_anonymous(client):
    response = client.get("/form")
    assert response.status_code == 200  # redirect to /login is followed
    assert response.url.path == "/login"


def test_form_has_logout_control(client, session: Session):
    register(client)
    client.post(
        "/login",
        data={"login_email": VALID["login_email"], "password": VALID["password"]},
    )

    response = client.get("/form")
    assert response.status_code == 200
    assert b'action="/logout"' in response.content


def test_login_page_redirects_to_form_when_logged_in(client, session: Session):
    register(client)
    client.post(
        "/login",
        data={"login_email": VALID["login_email"], "password": VALID["password"]},
    )

    response = client.get("/login")
    assert response.status_code == 200  # redirect to /form is followed
    assert response.url.path == "/form"


def test_register_page_redirects_to_form_when_logged_in(client, session: Session):
    register(client)
    client.post(
        "/login",
        data={"login_email": VALID["login_email"], "password": VALID["password"]},
    )

    response = client.get("/register")
    assert response.status_code == 200  # redirect to /form is followed
    assert response.url.path == "/form"
