"""Tests for GET /{username}: the public, read-only Portfolio page."""

from sqlmodel import Session

from main import Education, Info, Language, Project, ProfessionalExperience, Skill, User


def _create_user(session: Session, username: str = "alice-dev") -> User:
    user = User(
        username=username,
        login_email=f"{username}@example.com",
        hashed_password="not-a-real-hash",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_portfolio_renders_for_existing_user(client, session: Session):
    user = _create_user(session)
    session.add(Info(first_name="Alice", last_name="Dev", user_id=user.id))
    session.add(Education(school="EPF", degree="Ing", user_id=user.id))
    session.add(
        ProfessionalExperience(company="Acme", position="Dev", user_id=user.id)
    )
    session.add(Skill(software="Python", level="Expert", user_id=user.id))
    session.add(Language(language_name="Anglais", level="C1", user_id=user.id))
    session.add(Project(name_project="CV Generator", user_id=user.id))
    session.commit()

    response = client.get("/alice-dev")

    assert response.status_code == 200
    assert b"Alice" in response.content
    assert b"EPF" in response.content
    assert b"Acme" in response.content
    assert b"Python" in response.content
    assert b"Anglais" in response.content
    assert b"CV Generator" in response.content


def test_portfolio_has_no_edit_or_delete_controls(client, session: Session):
    user = _create_user(session)
    session.add(Info(first_name="Alice", last_name="Dev", user_id=user.id))
    session.add(Education(school="EPF", user_id=user.id))
    session.add(Skill(software="Python", level="Expert", user_id=user.id))
    session.commit()

    response = client.get("/alice-dev")

    assert response.status_code == 200
    assert b"/delete" not in response.content
    assert b"Supprimer" not in response.content
    assert b"/form" not in response.content


def test_portfolio_is_scoped_to_the_matching_user_only(client, session: Session):
    alice = _create_user(session, "alice-dev")
    bob = _create_user(session, "bob-dev")
    session.add(Info(first_name="Alice", last_name="Owner", user_id=alice.id))
    session.add(Info(first_name="Bob", last_name="Other", user_id=bob.id))
    session.add(Education(school="Alice School", user_id=alice.id))
    session.add(Education(school="Bob School", user_id=bob.id))
    session.commit()

    response = client.get("/alice-dev")

    assert response.status_code == 200
    assert b"Alice Owner" in response.content
    assert b"Alice School" in response.content
    assert b"Bob Other" not in response.content
    assert b"Bob School" not in response.content


def test_portfolio_unknown_username_returns_404(client, session: Session):
    response = client.get("/no-such-user")
    assert response.status_code == 404


def test_portfolio_renders_empty_for_brand_new_user(client, session: Session):
    _create_user(session, "brand-new")

    response = client.get("/brand-new")

    assert response.status_code == 200


def test_portfolio_omits_unset_optional_fields_instead_of_printing_none(
    client, session: Session
):
    user = _create_user(session)
    # first_name/last_name set, everything else left unset.
    session.add(Info(first_name="Alice", last_name="Dev", user_id=user.id))
    session.add(Education(school="EPF", user_id=user.id))
    session.add(Skill(software="Python", user_id=user.id))
    session.commit()

    response = client.get("/alice-dev")

    assert response.status_code == 200
    assert b"None" not in response.content


def test_portfolio_rejects_javascript_uri_in_links(client, session: Session):
    user = _create_user(session)
    session.add(
        Info(
            first_name="Alice",
            github="javascript:alert(document.cookie)",
            linkedin="https://linkedin.com/in/alice",
            user_id=user.id,
        )
    )
    session.add(
        Project(
            name_project="Evil",
            link="javascript:alert(1)",
            user_id=user.id,
        )
    )
    session.commit()

    response = client.get("/alice-dev")

    assert response.status_code == 200
    assert b"javascript:" not in response.content
    assert b'href="https://linkedin.com/in/alice"' in response.content
