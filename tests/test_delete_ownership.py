"""Tests for issue #7: ownership enforcement on deletion.

Covers: every delete route requires an authenticated User; deleting an item
the current User owns still succeeds; deleting another User's item (or a
non-existent id) returns 404 and leaves the data untouched.
"""

from sqlmodel import Session, select

from main import Education, Info, Language, Project, ProfessionalExperience, Skill
from tests.conftest import register_user


BOB = {
    "login_email": "bob@example.com",
    "password": "hunter2hunter2",
    "username": "bob-dev",
}


# path -> (model, data to create one row, field/value to confirm it survived
# a failed delete attempt untouched).
ENTITIES = {
    "info": (Info, {"first_name": "Alice"}, "first_name", "Alice"),
    "education": (Education, {"school": "EPF"}, "school", "EPF"),
    "professional_experience": (
        ProfessionalExperience,
        {"company": "Acme"},
        "company",
        "Acme",
    ),
    "skills": (Skill, {"software": "Python"}, "software", "Python"),
    "languages": (Language, {"language_name": "Anglais"}, "language_name", "Anglais"),
    "projects": (Project, {"name_project": "CV Generator"}, "name_project", "CV Generator"),
}


def _create_one_of_each(client):
    """Log in as Alice (registering her) and create one row per entity."""
    register_user(client)
    for path, (_, data, _, _) in ENTITIES.items():
        client.post(f"/{path}", data=data)


def test_every_delete_route_redirects_anonymous_to_login(client, session: Session):
    _create_one_of_each(client)
    client.cookies.clear()

    for path, (model, _, _, _) in ENTITIES.items():
        item = session.exec(select(model)).one()

        response = client.post(f"/{path}/{item.id}/delete")

        assert response.status_code == 200  # redirect to /login is followed
        assert response.url.path == "/login", path
        assert session.get(model, item.id) is not None, path


def test_owner_can_delete_own_item(client, session: Session):
    _create_one_of_each(client)

    for path, (model, _, _, _) in ENTITIES.items():
        item = session.exec(select(model)).one()

        response = client.post(f"/{path}/{item.id}/delete")

        assert response.status_code == 200, path
        assert session.get(model, item.id) is None, path


def test_other_user_cannot_delete_item_and_gets_404(client, session: Session):
    _create_one_of_each(client)
    client.cookies.clear()
    register_user(client, **BOB)

    for path, (model, _, field, value) in ENTITIES.items():
        item = session.exec(select(model)).one()

        response = client.post(f"/{path}/{item.id}/delete")

        assert response.status_code == 404, path
        surviving = session.get(model, item.id)
        assert surviving is not None, path
        assert getattr(surviving, field) == value, path


def test_deleting_nonexistent_item_returns_404(client, session: Session):
    register_user(client)

    for path in ENTITIES:
        response = client.post(f"/{path}/999999/delete")

        assert response.status_code == 404, path
