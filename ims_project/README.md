# Internship Management and Assessment System (IMS)

A full-stack, role-based web application built with **Python Django** and **PostgreSQL**
(SQLite by default for easy local grading) implementing the Software Requirement
Specification for the Internship Management and Assessment System.

## Features Implemented

- **Role-based access control** — System Admin, Department Admin, Faculty Mentor
  (acting as Faculty Coordinator), Evaluator, HoD/Programme Coordinator, Student —
  each with different permissions, including a strict Coordinator-only gate on
  approve/lock/edit-after-submission actions.
- **Student Profile Module** — degree start/end dates instead of repeated year-wise
  records, status tracking, bulk filtering, and bulk Excel/CSV import.
- **Break/Gap Management** — academic, internship, medical breaks with date validation
  against the degree period.
- **Organisation/Advocate Database** — reusable directory of law firms, NGOs, courts,
  companies, government offices with student-count tracking.
- **Internship Record Management** — regular/assessment/additional/repeated internship
  types, document upload, Save Draft / Submit distinction, reporting officer and
  stipend details, verification workflow with an approval timeline.
- **Faculty Mentor Assignment** — full history with effective-from/to dates, supports
  mid-semester mentor changes.
- **Fixed-Structure Marks Entry (Worksheet/Viva/Certificate/PPO)** — Evaluator
  enters marks and submits (cannot edit afterward); Faculty Coordinator reviews,
  can edit, then approves and locks. Every edit is recorded for audit purposes.
- **Final Year Calculation Engine** — the exact 5-step Best-7-of-8 process from
  the project's SRS (see below), shown on the marks summary page, the printable
  and PDF-exportable score card, and the batch-wise marks report/Excel export.
- **Reports & Dashboards** — student-wise, batch-wise, organisation-wise, mentor-wise,
  pending-marks/pending-document reports; KPI-card and chart-driven admin dashboard;
  Excel and PDF export.
- **Email Automation** — automatic thank-you email to the hosting organisation when
  a Faculty Coordinator approves an internship.
- **Notifications** — role-aware pending-items list for every role.
- **Activity/Audit Log** — tracks logins/logouts (with IP), creates, edits,
  approvals, locks, and email sends across the system.
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

### 2a. (Optional) Configure real email delivery
By default, the Email Automation Module (organisation thank-you emails)
prints to the console — no setup needed for local testing. For real
delivery in production:
```bash
export USE_SMTP_EMAIL=True
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=your-email@gmail.com
export SMTP_PASSWORD=your-app-password
export SMTP_FROM_EMAIL=your-email@gmail.com
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

### Final Year Calculation Engine (5-Step Process)

Implemented in `assessments/calculations.py`, following the exact 5-step
process from the project's SRS:

```
Step 1: Take the 8 regular internship totals (each scored out of 100 via
        Worksheet 0-40 + Viva 0-40 + Certificate 0-20)
Step 2: Pick the BEST 7 of those 8 automatically — the single lowest is dropped
Step 3: Calculate the average — Best 7 Total / 7
Step 4: Convert to a 70-mark scale — Average x 70 / 100
Step 5: Add the Assessment Internship score (scored directly out of 30,
        via Worksheet 0-10 + Viva 0-5 + Certificate 0-5 + PPO 0-10)

Final Internship Marks = Regular Component (out of 70) + Assessment Internship (out of 30)
```

If the assessment internship hasn't been marked yet, the final score falls
back to the regular component alone (out of 70) and is labelled
**Provisional** everywhere it's shown (marks summary, score card, batch
report, Excel/PDF export) so results remain useful before the 5th year
without being mistaken for a final number.

This appears in:
- `/assessments/summary/<student_id>/` — full breakdown with which 7 of 8 marks counted and the step-by-step engine visualised
- `/assessments/scorecard/<student_id>/` — printable consolidated score card
- `/assessments/scorecard/<student_id>/pdf/` — the same score card as a downloadable PDF
- `/reports/marks/` and its Excel export — batch-wide view of Best-7 avg, regular component, assessment mark, and final score

### Marks Entry & Approval Workflow (Evaluator → Coordinator)

The fixed marks structure (`assessments/models.py: InternshipMarks`) has two
scoring schemes depending on internship type, matching the SRS exactly:

| Component | Regular Internship (Years 1-4) | Assessment Internship (Year 5) |
|---|---|---|
| Worksheet | 0-40 | 0-10 |
| Viva | 0-40 | 0-5 |
| Certificate | 0-20 | 0-5 |
| PPO | — | 0-10 |
| **Total** | **100** | **30** |

Workflow:
1. **Faculty Evaluator** opens the internship, enters marks, and submits
   (`/assessments/internship/<id>/add/`). Once submitted, the Evaluator can
   no longer edit — only view.
2. **Faculty Coordinator** reviews the submitted marks
   (`/assessments/<marks_id>/review/`), can edit them if needed, then
   **Approve** or **Approve & Lock**. Locking also locks the parent
   internship record. Every edit at this stage is recorded in
   `MarkEditHistory` for audit purposes.

Role permissions for this are centralized in `accounts/models.py`
(`is_coordinator`, `is_evaluator_role`) and enforced via the
`coordinator_required` decorator in `accounts/decorators.py` — the existing
`faculty_mentor` role plays the Coordinator part, `evaluator` plays the
Evaluator part, and admins/HoD can always act as Coordinator.

### Dashboard KPIs & Charts

The System Admin dashboard (`accounts/dashboard_views.py`) matches the SRS's
exact structure: four KPI card groups (Students, Internships, Marks,
Organisations, each with 2-3 sub-metrics) and three Chart.js visualisations
(Internship Completion by Year, Marks Analysis showing average/highest/lowest,
and a Pending Activities breakdown).

### Bulk Student Import (Excel/CSV)

`/students/import/` accepts `.xlsx` or `.csv` files with columns
`register_number, name, email, mobile, programme_code, batch_name,
degree_start_date, degree_end_date, status`. Programme and batch must
already exist — rows referencing an unknown programme/batch, or a
register number that already exists, are skipped with a clear per-row
error message rather than failing the whole import.

### Email Automation

When a Faculty Coordinator approves an internship record
(`internships/views.py: internship_verify`), the system automatically
emails the organisation's contact (per `internships/notifications.py`)
thanking them for hosting the student, including student name, programme,
and internship duration — matching the SRS's Email Automation Module exactly.
The email fires only on the transition *into* `approved` (not on every
subsequent save), and gracefully skips (with an audit log entry and a
warning message to the Coordinator) if the organisation has no email on
file, rather than blocking the approval.

By default, emails print to the console (`EMAIL_BACKEND` in `settings.py`)
so this works out of the box with no setup. Set `USE_SMTP_EMAIL=True` plus
`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL` env
vars for real delivery.

### Notifications

`/accounts/notifications/` surfaces role-relevant pending items — pending
verifications and approvals for Admins/Coordinators, marks-ready-for-entry
for Evaluators, and corrections/published-marks for Students.

### Audit Log

Beyond the create/edit/approve/lock actions already logged throughout the
app, user login and logout are also recorded in `ActivityLog`
(`/accounts/activity-log/`) along with the client IP address.
