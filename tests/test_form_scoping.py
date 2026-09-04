"""Tests for issue #6: /form and the creation routes scoped to the current User.

Covers: every creation route requires a session and stamps `user_id`; `/form`
renders only the logged-in User's own entries; `POST /info` upserts instead
of inserting a second row.
"""

from sqlmodel import Session, select

from main import Education, Info, Language, Project, ProfessionalExperience, Skill, User
from tests.conftest import register_user


BOB = {
    "login_email": "bob@example.com",
    "password": "hunter2hunter2",
    "username": "bob-dev",
}


CREATION_ROUTES = {
    "/skills": {"software": "Python", "level": "Expert"},
    "/education": {"school": "EPF", "degree": "Ing"},
    "/professional_experience": {"company": "Acme", "position": "Dev"},
    "/languages": {"language_name": "Anglais", "level": "C1"},
    "/projects": {"name_project": "CV Generator"},
    "/info": {"first_name": "Alice"},
}


def test_every_creation_route_redirects_anonymous_to_login(client):
    for path, data in CREATION_ROUTES.items():
        response = client.post(path, data=data)
        assert response.status_code == 200  # redirect to /login is followed
        assert response.url.path == "/login", path


def test_created_skill_carries_current_user_id(client, session: Session):
    register_user(client)
    user = session.exec(select(User)).one()

    client.post("/skills", data={"software": "Python", "level": "Expert"})

    skill = session.exec(select(Skill)).one()
    assert skill.user_id == user.id


def test_created_education_carries_current_user_id(client, session: Session):
    register_user(client)
    user = session.exec(select(User)).one()

    client.post("/education", data={"school": "EPF"})

    row = session.exec(select(Education)).one()
    assert row.user_id == user.id


def test_created_professional_experience_carries_current_user_id(
    client, session: Session
):
    register_user(client)
    user = session.exec(select(User)).one()

    client.post("/professional_experience", data={"company": "Acme"})

    row = session.exec(select(ProfessionalExperience)).one()
    assert row.user_id == user.id


def test_created_language_carries_current_user_id(client, session: Session):
    register_user(client)
    user = session.exec(select(User)).one()

    client.post("/languages", data={"language_name": "Anglais"})

    row = session.exec(select(Language)).one()
    assert row.user_id == user.id


def test_created_project_carries_current_user_id(client, session: Session):
    register_user(client)
    user = session.exec(select(User)).one()

    client.post("/projects", data={"name_project": "CV Generator"})

    row = session.exec(select(Project)).one()
    assert row.user_id == user.id


def test_created_info_carries_current_user_id(client, session: Session):
    register_user(client)
    user = session.exec(select(User)).one()

    client.post("/info", data={"first_name": "Alice"})

    row = session.exec(select(Info)).one()
    assert row.user_id == user.id


def test_form_shows_only_the_logged_in_users_own_entries(client, session: Session):
    alice = register_user(client)
    client.post("/education", data={"school": "Alice School"})
    client.cookies.clear()

    register_user(client, **BOB)
    client.post("/education", data={"school": "Bob School"})
    client.cookies.clear()

    client.post(
        "/login",
        data={"login_email": alice["login_email"], "password": alice["password"]},
    )
    response = client.get("/form")

    assert response.status_code == 200
    assert b"Alice School" in response.content
    assert b"Bob School" not in response.content


def test_info_second_submit_updates_in_place_instead_of_inserting(
    client, session: Session
):
    register_user(client)

    client.post(
        "/info",
        data={"first_name": "Alice", "contact_email": "alice@old.example.com"},
    )
    client.post(
        "/info",
        data={"first_name": "Alice", "contact_email": "alice@new.example.com"},
    )

    rows = session.exec(select(Info)).all()
    assert len(rows) == 1
    assert rows[0].contact_email == "alice@new.example.com"


def test_info_first_submit_creates_when_user_has_none(client, session: Session):
    register_user(client)

    assert session.exec(select(Info)).all() == []

    client.post("/info", data={"first_name": "Alice"})

    rows = session.exec(select(Info)).all()
    assert len(rows) == 1
    assert rows[0].first_name == "Alice"


def test_form_renders_delete_control_for_own_entries(client, session: Session):
    register_user(client)
    client.post("/education", data={"school": "EPF"})

    response = client.get("/form")

    assert response.status_code == 200
    edu = session.exec(select(Education)).one()
    assert f'action="/education/{edu.id}/delete"'.encode() in response.content
