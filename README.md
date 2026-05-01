# 📄 Portfolio Builder — FastAPI + SQLite + Jinja2

Une application web minimaliste pour créer et afficher son portfolio en ligne. Tu remplis un formulaire, et ton portfolio se génère automatiquement.

---

## ✨ Fonctionnalités

- Formulaire structuré pour saisir toutes les informations de ton CV
- Affichage dynamique du portfolio via des templates Jinja2
- Persistance des données avec SQLite via SQLModel
- Architecture légère : zéro JavaScript côté client, tout en HTML/CSS
- Deux vues : `/form` pour éditer, `/` pour visualiser

---

## 🗂️ Structure du projet

```
portfolio/
├── main.py                  # Application FastAPI (routes + modèles)
├── cv.db                    # Base de données SQLite (générée au démarrage)
├── templates/
│   ├── form.html            # Formulaire de saisie
│   └── index.html           # Vue portfolio
├── static/
│   └── style.css            # Styles CSS
└── README.md
```

---

## 🧱 Modèles de données

| Modèle | Champs |
|---|---|
| `Info` | first_name, last_name, email, phone, location, linkedin, github |
| `ProfessionalExperience` | company, position, start_date, end_date, description |
| `Education` | school, degree, field_of_study, start_year, end_year |
| `Skill` | software, level |
| `Language` | language_name, level |
| `Project` | name_project, description, link |

---

## 🚀 Installation & Lancement

### 1. Cloner le repo

```bash
git clone https://github.com/ton-user/portfolio.git
cd portfolio
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Installer les dépendances

```bash
pip install fastapi uvicorn sqlmodel jinja2 python-multipart
```

### 4. Lancer l'application

```bash
uvicorn main:app --reload
```

L'application est accessible sur [http://localhost:8000](http://localhost:8000).

---

## 🔗 Routes

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/` | Affiche le portfolio |
| `GET` | `/form` | Affiche le formulaire de saisie |
| `POST` | `/info` | Ajoute les informations personnelles |
| `POST` | `/professional_experience` | Ajoute une expérience professionnelle |
| `POST` | `/education` | Ajoute une formation |
| `POST` | `/skills` | Ajoute une compétence |
| `POST` | `/languages` | Ajoute une langue |
| `POST` | `/projects` | Ajoute un projet |

---

## 🖼️ Aperçu des pages

### `/form` — Formulaire de saisie
Permet de renseigner section par section :
1. **Profil** — nom, prénom, email, téléphone, localisation, GitHub, LinkedIn
2. **Expérience** — poste, entreprise, dates, description
3. **Formation** — école, diplôme, spécialité, années
4. **Compétences** — logiciel/compétence + niveau (Expert → Débutant)
5. **Langues** — langue + niveau (Natif → A2)
6. **Projets** — nom, description, lien

### `/` — Portfolio généré
Affiche les données sous forme de portfolio avec :
- Hero section (nom, poste, coordonnées, liens)
- Sections expériences, formations, compétences, langues, projets

---

## 🛠️ Stack technique

| Composant | Technologie |
|---|---|
| Framework web | [FastAPI](https://fastapi.tiangolo.com/) |
| ORM / Base de données | [SQLModel](https://sqlmodel.tiangolo.com/) + SQLite |
| Templates | [Jinja2](https://jinja.palletsprojects.com/) |
| Serveur ASGI | [Uvicorn](https://www.uvicorn.org/) |
| CSS | Vanilla CSS (fichier `style.css`) |

---

## 📦 Dépendances (`requirements.txt`)

```
fastapi
uvicorn[standard]
sqlmodel
jinja2
python-multipart
```

Générer le fichier :
```bash
pip freeze > requirements.txt
```

---

## 📝 Notes

- La base de données `cv.db` est créée automatiquement au premier démarrage.
- Chaque soumission de formulaire **ajoute** une entrée — il n'y a pas encore de système d'édition ou de suppression.
- La section Profil (`Info`) peut contenir plusieurs entrées ; seule la première est affichée dans le portfolio.
- Pour repartir de zéro, supprimer le fichier `cv.db` et relancer l'application.

---

## 🔮 Améliorations possibles

- Ajout d'un système d'édition et suppression des entrées
- Authentification pour protéger le formulaire
- Export PDF du portfolio
- Plusieurs thèmes CSS
- Déploiement sur Railway, Render ou Fly.io

---

## 📄 Licence

MIT — libre d'utilisation et de modification.