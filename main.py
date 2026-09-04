import os
import re
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, Session, SQLModel, create_engine, select
from starlette.middleware.sessions import SessionMiddleware

def safe_url(value: str | None) -> str:
    """An http(s) URL as-is, or '' for anything else (blank, javascript:, data:, ...).

    Guards template `href`s built from free-text user input (Info.github,
    Info.linkedin, Project.link) against script-scheme injection — a link
    rendered on someone else's public Portfolio must not be able to execute
    script in a visitor's browser.
    """
    if value and value.startswith(("http://", "https://")):
        return value
    return ""


templates = Jinja2Templates(directory="templates")
templates.env.filters["safe_url"] = safe_url
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# A precomputed hash to run through pwd_context.verify() when no matching User
# exists, so an unknown login_email takes the same bcrypt-verify time as a
# known one — otherwise the two cases are distinguishable by response latency.
_DUMMY_PASSWORD_HASH = pwd_context.hash("no-such-user-timing-safety")

# Usernames double as the Portfolio URL segment (`/username`), so any value
# that collides with an existing top-level route is rejected at registration.
RESERVED_USERNAMES = {
    "form",
    "login",
    "logout",
    "register",
    "static",
    "docs",
    "redoc",
    "openapi",
    "openapi.json",
    "favicon.ico",
    "skills",
    "education",
    "professional_experience",
    "languages",
    "info",
    "projects",
}
USERNAME_PATTERN = re.compile(r"^[a-z0-9-]{3,30}$")

sqlite_url = "sqlite:///./cv.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    login_email: str = Field(unique=True, index=True)
    hashed_password: str


def get_current_user(request: Request, session: SessionDep) -> User | None:
    user_id = request.session.get("user_id")
    if user_id is None:
        return None
    return session.get(User, user_id)


CurrentUserDep = Annotated[User | None, Depends(get_current_user)]


def redirect_if_anonymous(current_user: User | None) -> RedirectResponse | None:
    """Auth gate for routes that require a session, e.g. /form."""
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    return None


def redirect_if_authenticated(current_user: User | None) -> RedirectResponse | None:
    """Guard for routes that only make sense signed out, e.g. /login, /register."""
    if current_user is not None:
        return RedirectResponse(url="/form", status_code=303)
    return None


class Skill(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    software: str | None = None
    level: str | None = None
    user_id: int | None = Field(default=None, foreign_key="user.id")


class Education(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    school: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_year: int | None = None
    end_year: int | None = None
    user_id: int | None = Field(default=None, foreign_key="user.id")


class ProfessionalExperience(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    company: str | None = None
    position: str | None = None
    start_date: int | None = None
    end_date: int | None = None
    description: str | None = None
    user_id: int | None = Field(default=None, foreign_key="user.id")


class Language(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    language_name: str | None = None
    level: str | None = None
    user_id: int | None = Field(default=None, foreign_key="user.id")


class Info(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    github: str | None = None
    user_id: int | None = Field(default=None, foreign_key="user.id")


class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name_project: str | None = None
    description: str | None = None
    link: str | None = None
    user_id: int | None = Field(default=None, foreign_key="user.id")


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


@app.get("/register", response_class=HTMLResponse)
def read_register(request: Request, current_user: CurrentUserDep):
    if (redirect := redirect_if_authenticated(current_user)) is not None:
        return redirect
    return templates.TemplateResponse(request, "register.html", context={})


@app.post("/register")
def create_user(
    request: Request,
    login_email: str = Form(...),
    password: str = Form(...),
    username: str = Form(...),
    session: SessionDep = None,
):
    def reject(error: str):
        return templates.TemplateResponse(
            request,
            "register.html",
            context={
                "error": error,
                "login_email": login_email,
                "username": username,
            },
        )

    if not USERNAME_PATTERN.match(username):
        return reject(
            "Nom d'utilisateur invalide : lettres minuscules, chiffres et "
            "tirets uniquement, 3 à 30 caractères."
        )

    if username in RESERVED_USERNAMES:
        return reject("Ce nom d'utilisateur est réservé.")

    if session.exec(select(User).where(User.username == username)).first():
        return reject("Ce nom d'utilisateur est déjà pris.")

    if session.exec(select(User).where(User.login_email == login_email)).first():
        return reject("Cet email est déjà utilisé.")

    user = User(
        username=username,
        login_email=login_email,
        hashed_password=pwd_context.hash(password),
    )
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        # Another request won a race against the checks above and took this
        # username/login_email first between the SELECTs and this commit.
        session.rollback()
        return reject("Ce nom d'utilisateur ou cet email est déjà pris.")
    session.refresh(user)

    request.session["user_id"] = user.id

    return RedirectResponse(url="/form", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def read_login(request: Request, current_user: CurrentUserDep):
    if (redirect := redirect_if_authenticated(current_user)) is not None:
        return redirect
    return templates.TemplateResponse(request, "login.html", context={})


@app.post("/login")
def create_login(
    request: Request,
    login_email: str = Form(...),
    password: str = Form(...),
    session: SessionDep = None,
):
    def reject():
        return templates.TemplateResponse(
            request,
            "login.html",
            context={
                "error": "Email ou mot de passe incorrect.",
                "login_email": login_email,
            },
        )

    user = session.exec(
        select(User).where(User.login_email == login_email)
    ).first()
    # Always run a bcrypt verify, even for an unknown email, so the two cases
    # take the same amount of time and can't be told apart by response latency.
    password_ok = pwd_context.verify(
        password, user.hashed_password if user else _DUMMY_PASSWORD_HASH
    )
    if user is None or not password_ok:
        return reject()

    request.session["user_id"] = user.id
    return RedirectResponse(url="/form", status_code=303)


@app.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@app.get("/form", response_class=HTMLResponse)
def read_form(request: Request, current_user: CurrentUserDep):
    if (redirect := redirect_if_anonymous(current_user)) is not None:
        return redirect
    return templates.TemplateResponse(request, "form.html", context={})


@app.get("/", response_class=HTMLResponse)
def read_home(request: Request, current_user: CurrentUserDep):
    if (redirect := redirect_if_authenticated(current_user)) is not None:
        return redirect
    return templates.TemplateResponse(request, "home.html", context={})


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


@app.post("/education/{item_id}/delete")
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


def _scoped(session: Session, model: type, user_id: int | None) -> list:
    """All rows of `model` belonging to a User, in a stable (insertion) order."""
    return session.exec(
        select(model).where(model.user_id == user_id).order_by(model.id)
    ).all()


# Registered last so every fixed route above (/, /form, /login, /register,
# /logout, /static, the entity routes, …) is matched first — route order,
# not just RESERVED_USERNAMES, is what keeps a Username from ever shadowing
# one of them.
@app.get("/{username}", response_class=HTMLResponse)
def read_portfolio(username: str, request: Request, session: SessionDep):
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise HTTPException(status_code=404)

    return templates.TemplateResponse(
        request,
        "portfolio.html",
        context={
            "info": _scoped(session, Info, user.id),
            "education": _scoped(session, Education, user.id),
            "professional_experience": _scoped(
                session, ProfessionalExperience, user.id
            ),
            "skills": _scoped(session, Skill, user.id),
            "languages": _scoped(session, Language, user.id),
            "projects": _scoped(session, Project, user.id),
        },
    )
