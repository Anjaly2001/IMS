# Internship Management and Assessment System (IMS)

A full-stack, role-based web application built with **Python Django** and **PostgreSQL**
(SQLite by default for easy local grading) implementing the Software Requirement
Specification for the Internship Management and Assessment System.

## Features Implemented

- **Role-based access control** — System Admin, Department Admin, Faculty Mentor,
  Evaluator, HoD/Programme Coordinator, Student — each with different permissions.
- **Student Profile Module** — degree start/end dates instead of repeated year-wise
  records, status tracking, bulk filtering.
- **Break/Gap Management** — academic, internship, medical breaks with date validation
  against the degree period.
- **Organisation/Advocate Database** — reusable directory of law firms, NGOs, courts,
  companies, government offices with student-count tracking.
- **Internship Record Management** — regular/assessment/additional/repeated internship
  types, document upload, verification workflow.
- **Faculty Mentor Assignment** — full history with effective-from/to dates, supports
  mid-semester mentor changes.
- **Intermediate + Final Viva Marks** — configurable assessment types, max-marks
  validation, mark locking, edit history/audit trail.
- **Marks Consolidation** — Best 7-of-8 regular internship average, combined with
  the 5th-year assessment internship using a 70:30 weighted final score
  (`assessments/calculations.py`), shown on the marks summary page, the printable
  score card, the batch-wise marks report, and the Excel export.
- **Reports & Dashboards** — student-wise, batch-wise, organisation-wise, mentor-wise,
  pending-marks/pending-document reports; Excel export.
- **Activity/Audit Log** — tracks key actions across the system.
- **Responsive Bootstrap 5 UI** — sidebar navigation, mobile-friendly, clean
  university-appropriate visual design (navy/gold palette).

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Django 5.x |
| Database | PostgreSQL (SQLite fallback for local dev) |
| Frontend | Bootstrap 5, Bootstrap Icons, vanilla JS |
| Reports | openpyxl (Excel), reportlab (PDF-ready) |
| Auth | Django's built-in auth with a custom `User` model (role field) |

## Project Structure

```
ims_project/
├── ims_project/        # Project settings, root URLs
├── accounts/            # Custom User model, auth, dashboard, activity log
├── students/             # Student profiles, programmes, batches, breaks
├── organisations/        # Organisation/advocate database
├── internships/           # Internship records, mentor assignments
├── assessments/            # Marks entry, locking, edit history
├── reports/                 # Reports & Excel export
├── templates/                # All HTML templates (base.html + per-app)
├── static/                    # CSS/JS (Bootstrap loaded via CDN)
├── requirements.txt
└── manage.py
```

## Setup Instructions

### 1. Create a virtual environment & install dependencies
```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. (Optional) Configure PostgreSQL
By default the project uses **SQLite** so it runs with zero extra setup —
perfect for grading/demoing. To use PostgreSQL instead:

```bash
# Create the database and user in psql:
#   CREATE DATABASE ims_db;
#   CREATE USER ims_user WITH PASSWORD 'ims_password';
#   GRANT ALL PRIVILEGES ON DATABASE ims_db TO ims_user;

export USE_POSTGRES=True
export DB_NAME=ims_db
export DB_USER=ims_user
export DB_PASSWORD=ims_password
export DB_HOST=localhost
export DB_PORT=5432
```

### 3. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create your System Admin account
The database starts completely empty — no demo students, organisations, or
internship records. Run this once to create the first login:

```bash
python manage.py create_admin
```

It will prompt for a username, optional name/email, and a password
(entered twice, hidden). You can also pass details as flags and only be
prompted for the password:

```bash
python manage.py create_admin --username admin --email admin@yourcollege.edu --first-name System --last-name Administrator
```

This creates exactly one account — a System Admin with full access to every
module. Everything else (programmes, batches, organisations, students, faculty
accounts, internship records, marks) is entered through the website itself.

A sensible first-time data entry order:
1. **Students → Programmes** — add your programme(s), e.g. B.A. LL.B. (Hons.)
2. **Students → Batches** — add the batch(es) under each programme
3. **User Management** — create accounts for faculty mentors, evaluators, HoD,
   and department admins (so you can assign them as mentors/evaluators later)
4. **Organisations** — add law firms, NGOs, courts, etc. as placements are confirmed
5. **Students** — add student profiles
6. **Internship Records, Mentor Assignments, Marks** — as the term progresses

### 5. Run the development server
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000/** and log in with the System Admin account you created.

### 6. (Alternative) Django's built-in createsuperuser
`python manage.py create_admin` is the recommended way to create the first
login, but Django's standard `createsuperuser` command also works — any
superuser automatically gets full System Admin access (see Permission Model
below), no manual role editing required:
```bash
python manage.py createsuperuser
```

## Key URLs

| URL | Purpose |
|---|---|
| `/accounts/login/` | Login |
| `/dashboard/` | Role-based dashboard |
| `/students/` | Student list/profiles |
| `/organisations/` | Organisation/advocate directory |
| `/internships/` | Internship records |
| `/internships/mentors/` | Mentor assignments |
| `/reports/` | Reports hub (student/marks/org/mentor/pending) |
| `/accounts/users/` | User management (admin only) |
| `/admin/` | Django admin panel |

## Notes for Evaluators

- All forms include server-side validation (marks ≤ max marks, break dates within
  degree period, etc.) as specified in the SRS validation rules (VR-01 to VR-12).
- Marks, once locked, cannot be edited through the UI (`FR-AS-08`, `NFR-SEC-06`).
- The `ActivityLog` model satisfies the audit/logging requirements (Section 10 of the SRS).
- The data model maps directly to the suggested database tables in Section 7 of the SRS
  (`students`, `organisations`, `internship_records`, `break_records`,
  `mentor_assignments`, `assessment_marks`, plus Django's built-in auth tables for users).

### Permission Model

A Django **superuser** (created via `createsuperuser` or `User.objects.create_superuser`)
always has full, unrestricted access to every module — listing pages, create/edit forms,
reports, and User Management — regardless of what its `role` field says. This is enforced
in `accounts/models.py`:

- `User.save()` automatically sets `role='system_admin'` for any superuser, so the role
  field and `is_superuser` flag never fall out of sync.
- `is_admin`, `is_system_admin`, and `is_student_role` are computed properties that all
  view-level decorators (`accounts/decorators.py`) and templates use consistently —
  there's no scattered `role == 'student'` logic that a superuser could fall through.

Role hierarchy for access purposes:

| Role | Access |
|---|---|
| System Admin / Django superuser | Everything — all modules, all filters, User Management |
| Department Admin | Everything except User Management (same as System Admin elsewhere) |
| Faculty Mentor / Evaluator / HoD | Students, Internships, Organisations, Reports (filtered to their own assignments where relevant) |
| Student | Own profile and own internship records only |

### Create/Edit Redirect Convention

Every "Add" or "Edit" form for a top-level entity (Student, Organisation, Internship
Record, User, Programme, Batch) redirects back to that entity's **listing page** on
success — never to the detail page. This keeps the workflow consistent: add a record,
land back on the list, see it there, move to the next one.

Sub-resources that don't have their own standalone list page (breaks, mentor
assignments made from a student's page, assessment marks) redirect back to the
parent record's detail page instead, since that detail page *is* their natural
listing context.

### Final Score Calculation (Best 7 of 8 + 70:30)

Implemented in `assessments/calculations.py`:

```
Regular Internship Score   = average of the BEST 7 of the 8 regular internship
                              viva marks (out of 100 each); the single lowest
                              mark is dropped automatically
Assessment Internship Score = viva mark of the 5th-year, 3-month assessment
                              internship (out of 100)
Final Consolidated Score    = 0.70 x Regular Internship Score
                             + 0.30 x Assessment Internship Score
```

If the assessment internship hasn't been marked yet, the final score falls back
to the regular average alone and is labelled **Provisional** everywhere it's shown
(marks summary, score card, batch report, Excel export) so results remain useful
before the 5th year without being mistaken for a final number.

This appears in three places:
- `/assessments/summary/<student_id>/` — full breakdown with which 7 of 8 marks counted
- `/assessments/scorecard/<student_id>/` — printable consolidated score card
- `/reports/marks/` and its Excel export — batch-wide view of Best-7 avg, assessment mark, and final score
