from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated

templates = Jinja2Templates(directory="templates")
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

sqlite_url = "sqlite:///./cv.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


class Skill(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    software: str | None = None
    level: str | None = None


class Education(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    school: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_year: int | None = None
    end_year: int | None = None


class ProfessionalExperience(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    company: str | None = None
    position: str | None = None
    start_date: int | None = None
    end_date: int | None = None
    description: str | None = None


class Language(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    language_name: str | None = None
    level: str | None = None


class Info(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    github: str | None = None


class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name_project: str | None = None
    description: str | None = None
    link: str | None = None


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.post("/skills")
def create_skill(
    software: str | None = Form(None),
    level: str | None = Form(None),
    session: SessionDep = None,
):
    session.add(Skill(software=software, level=level))
    session.commit()
    return RedirectResponse(url="/form", status_code=303)


@app.post("/education")
def create_education(
    school: str | None = Form(None),
    degree: str | None = Form(None),
    field_of_study: str | None = Form(None),
    start_year: int | None = Form(None),
    end_year: int | None = Form(None),
    session: SessionDep = None,
):
    session.add(
        Education(
            school=school,
            degree=degree,
            field_of_study=field_of_study,
            start_year=start_year,
            end_year=end_year,
        )
    )
    session.commit()
    return RedirectResponse(url="/form", status_code=303)


@app.post("/professional_experience")
def create_professional_experience(
    company: str | None = Form(None),
    position: str | None = Form(None),
    start_date: int | None = Form(None),
    end_date: int | None = Form(None),
    description: str | None = Form(None),
    session: SessionDep = None,
):
    session.add(
        ProfessionalExperience(
            company=company,
            position=position,
            start_date=start_date,
            end_date=end_date,
            description=description,
        )
    )
    session.commit()
    return RedirectResponse(url="/form", status_code=303)


@app.post("/languages")
def create_language(
    language_name: str | None = Form(None),
    level: str | None = Form(None),
    session: SessionDep = None,
):
    session.add(Language(language_name=language_name, level=level))
    session.commit()
    return RedirectResponse(url="/form", status_code=303)


@app.post("/info")
def create_info(
    first_name: str | None = Form(None),
    last_name: str | None = Form(None),
    email: str | None = Form(None),
    phone: str | None = Form(None),
    location: str | None = Form(None),
    linkedin: str | None = Form(None),
    github: str | None = Form(None),
    session: SessionDep = None,
):
    session.add(
        Info(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            location=location,
            linkedin=linkedin,
            github=github,
        )
    )
    session.commit()
    return RedirectResponse(url="/form", status_code=303)


@app.post("/projects")
def create_project(
    name_project: str | None = Form(None),
    description: str | None = Form(None),
    link: str | None = Form(None),
    session: SessionDep = None,
):
    session.add(Project(name_project=name_project, description=description, link=link))
    session.commit()
    return RedirectResponse(url="/form", status_code=303)


@app.get("/form", response_class=HTMLResponse)
def read_form(request: Request):
    return templates.TemplateResponse(request, "form.html", context={})


@app.get("/", response_class=HTMLResponse)
def read_home(request: Request, session: SessionDep):
    return templates.TemplateResponse(
        request,
        "index.html",
        context={
            "skills": session.exec(select(Skill)).all(),
            "education": session.exec(select(Education)).all(),
            "professional_experience": session.exec(
                select(ProfessionalExperience)
            ).all(),
            "languages": session.exec(select(Language)).all(),
            "info": session.exec(select(Info)).all(),
            "projects": session.exec(select(Project)).all(),
        },
    )


@app.post("/info/{item_id}/delete")
def delete_info(item_id: int, session: SessionDep):
    item = session.get(Info, item_id)
    session.delete(item)
    session.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/professional_experience/{item_id}/delete")
def delete_experience(item_id: int, session: SessionDep):
    item = session.get(ProfessionalExperience, item_id)
    session.delete(item)
    session.commit()
    return RedirectResponse(url="/", status_code=303)


@app.delete("/education/{item_id}")
def delete_education(item_id: int, session: SessionDep):
    item = session.get(Education, item_id)
    session.delete(item)
    session.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/skills/{item_id}/delete")
def delete_skill(item_id: int, session: SessionDep):
    item = session.get(Skill, item_id)
    session.delete(item)
    session.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/languages/{item_id}/delete")
def delete_language(item_id: int, session: SessionDep):
    item = session.get(Language, item_id)
    session.delete(item)
    session.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/projects/{item_id}/delete")
def delete_project(item_id: int, session: SessionDep):
    item = session.get(Project, item_id)
    session.delete(item)
    session.commit()
    return RedirectResponse(url="/", status_code=303)
