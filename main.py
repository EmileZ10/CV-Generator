from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated
from fastapi import Depends
from fastapi.staticfiles import StaticFiles

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
    software: str
    level: str


class Education(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    school: str
    degree: str
    field_of_study: str
    start_year: int
    end_year: int


class ProfessionalExperience(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    company: str
    position: str
    start_date: int
    end_date: int
    description: str


class Language(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    language_name: str
    level: str


class Info(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str
    phone: str
    location: str
    linkedin: str
    github: str


class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name_project: str
    description: str
    link: str


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.post("/skills")
def create_skill(software: str, level: str, session: SessionDep):
    skill = Skill(software=software, level=level)
    session.add(skill)
    session.commit()
    session.refresh(skill)
    return RedirectResponse(url="/", status_code=303)


@app.post("/education")
def create_education(
    school: str,
    degree: str,
    field_of_study: str,
    start_year: int,
    end_year: int,
    session: SessionDep,
):
    education = Education(
        school=school,
        degree=degree,
        field_of_study=field_of_study,
        start_year=start_year,
        end_year=end_year,
    )
    session.add(education)
    session.commit()
    session.refresh(education)
    return RedirectResponse(url="/", status_code=303)


@app.post("/professional_experience")
def create_professional_experience(
    company: str,
    position: str,
    start_date: int,
    end_date: int,
    description: str,
    session: SessionDep,
):
    experience = ProfessionalExperience(
        company=company,
        position=position,
        start_date=start_date,
        end_date=end_date,
        description=description,
    )
    session.add(experience)
    session.commit()
    session.refresh(experience)
    return RedirectResponse(url="/", status_code=303)


@app.post("/languages")
def create_language(language_name: str, level: str, session: SessionDep):
    language = Language(language_name=language_name, level=level)
    session.add(language)
    session.commit()
    session.refresh(language)
    return RedirectResponse(url="/", status_code=303)


@app.post("/info")
def create_info(
    first_name: str,
    last_name: str,
    email: str,
    phone: str,
    location: str,
    linkedin: str,
    github: str,
    session: SessionDep,
):
    info = Info(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        location=location,
        linkedin=linkedin,
        github=github,
    )
    session.add(info)
    session.commit()
    session.refresh(info)
    return RedirectResponse(url="/", status_code=303)


@app.post("/projects")
def create_project(name_project: str, description: str, link: str, session: SessionDep):
    project = Project(name_project=name_project, description=description, link=link)
    session.add(project)
    session.commit()
    session.refresh(project)
    return RedirectResponse(url="/", status_code=303)


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


# @app.delete("/skills/{skill_id}")
# def delete_skill(skill_id: int, session: SessionDep):
# skill = session.get(Skill, skill_id)
# if not skill:
#   raise HTTPException(status_code=404, detail="Skill not found")
# session.delete(skill)
# session.commit()
# return {"ok": True}
