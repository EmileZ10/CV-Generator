"""Smoke tests establishing the route-test template for the rest of the feature."""

from sqlmodel import Session, select

from main import Education


def test_form_page_renders(client):
    response = client.get("/form")
    assert response.status_code == 200


def test_home_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200


def test_create_education(client, session: Session):
    response = client.post("/education", data={"school": "EPF", "degree": "Ing"})
    assert response.status_code == 200  # redirect to /form is followed

    rows = session.exec(select(Education)).all()
    assert [r.school for r in rows] == ["EPF"]


def test_delete_education_uses_post_route(client, session: Session):
    session.add(Education(school="EPF"))
    session.commit()
    item_id = session.exec(select(Education)).one().id

    # The old `DELETE /education/{id}` route is gone.
    assert client.delete(f"/education/{item_id}").status_code in (404, 405)

    response = client.post(f"/education/{item_id}/delete")
    assert response.status_code == 200
    assert session.exec(select(Education)).all() == []
