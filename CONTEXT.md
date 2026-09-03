# CV-Generator

A FastAPI app where each User maintains exactly one public Portfolio, editable only by its owner and viewable by anyone at a stable URL.

## Language

**User**:
An authenticated account holder, identified by a Login Email and a password, who owns exactly one Portfolio.
_Avoid_: Account, Member

**Username**:
The public, immutable identifier a User chooses once at registration. Doubles as the Portfolio's URL segment (`/username`) and can never be changed afterward, so shared links stay valid forever. Certain values are reserved and rejected at registration because they would collide with existing application routes (e.g. `form`, `login`, `register`, `static`).
_Avoid_: Slug, Handle

**Portfolio**:
The public, read-only page at `/username`, composed of a User's Info, Education, ProfessionalExperience, Skill, Language, and Project records. Visible to anyone without authentication.
_Avoid_: CV, Resume, Profile

**Info**:
The single record per User holding personal/contact details (name, phone, location, links, Contact Email). Exactly one Info exists per User.
_Avoid_: Profile, Personal Info

**Login Email**:
The private email address a User authenticates with. Never displayed on the Portfolio.
_Avoid_: Account Email, Email

**Contact Email**:
The optional public email address on Info, shown on the Portfolio so visitors can reach the User. Independent of the Login Email — the two may differ, and either may be left blank.
_Avoid_: Info Email, Email
