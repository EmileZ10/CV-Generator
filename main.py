from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

app = FastAPI()

skills = []
education = []
professional_experience = []
languages = []
info = []
projects = []


class Skill(BaseModel):
    software: str
    level: str


class Education(BaseModel):
    school: str
    degree: str
    field_of_study: str
    start_year: int
    end_year: int


class ProfessionalExperience(BaseModel):
    company: str
    position: str
    start_date: int
    end_date: int
    description: str


class Language(BaseModel):
    language_name: str
    level: str


class Info(BaseModel):
    email: str
    phone: str
    location: str
    linkedin: str
    github: str


class Project(BaseModel):
    name_project: str
    description: str
    link: str


@app.post("/skills")
def create_skill(software: str, level: str):
    skill = {"software": software, "level": level}
    skills.append(skill)
    response = {"id": len(skills) - 1, "skill": skill}
    return response


@app.post("/education")
def create_education(
    school: str, degree: str, field_of_study: str, start_year: int, end_year: int
):
    education_dict = {
        "school": school,
        "degree": degree,
        "field_of_study": field_of_study,
        "start_year": start_year,
        "end_year": end_year,
    }
    education.append(education_dict)
    response = {"id": len(education) - 1, "education": education_dict}
    return response


@app.post("/professional_experience")
def create_professional_experience(
    company: str, position: str, start_date: int, end_date: int, description: str
):
    exp_dict = {
        "company": company,
        "position": position,
        "start_date": start_date,
        "end_date": end_date,
        "description": description,
    }
    professional_experience.append(exp_dict)
    response = {"id": len(professional_experience) - 1, "experience": exp_dict}
    return response


@app.post("/languages")
def create_language(language_name: str, level: str):
    lang_dict = {"language_name": language_name, "level": level}
    languages.append(lang_dict)
    response = {"id": len(languages) - 1, "language": lang_dict}
    return response


@app.post("/info")
def create_info(email: str, phone: str, location: str, linkedin: str, github: str):
    info_dict = {
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin": linkedin,
        "github": github,
    }
    info.append(info_dict)
    response = {"id": len(info) - 1, "info": info_dict}
    return response


@app.post("/projects")
def create_project(name_project: str, description: str, link: str):
    proj_dict = {"name_project": name_project, "description": description, "link": link}
    projects.append(proj_dict)
    response = {"id": len(projects) - 1, "project": proj_dict}
    return response


@app.get("/", response_class=HTMLResponse)
def read_home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        context={
            "skills": skills,
            "education": education,
            "professional_experience": professional_experience,
            "languages": languages,
            "info": info,
            "projects": projects,
        },
    )


@app.delete("/skills/{skill_id}")
def delete_skill(skill_id: int):
    if 0 <= skill_id < len(skills):
        deleted_skill = skills.pop(skill_id)
        return {"message": "Skill deleted successfully", "deleted_skill": deleted_skill}
    else:
        return {"error": "Skill not found"}
