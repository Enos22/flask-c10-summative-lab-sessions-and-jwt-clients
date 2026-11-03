# MediReminder Backend

## Description

MediReminder is a REST API backend for a medication reminder app. Users sign up, log in, and manage their own medications, the schedules for taking them, and a record of whether each dose was taken or missed. The API serves a React frontend and is built with Flask, Flask-SQLAlchemy, Flask-Migrate and Marshmallow, using SQLite for storage.

Every resource is owned by a user. Users can only see and change their own data.

<!-- TODO (team): confirm session-based auth is the final choice (the repo also ships a JWT client). -->
Authentication is session-based: logging in stores the user's id in the session, and protected routes return `401` when nobody is logged in.

### Data model

```
User  ->  Medication  ->  MedicationSchedule  ->  Dose
 1:many      1:many            1:many
```

| Model | Purpose |
|---|---|
| `User` | Account with a unique username and a hashed password |
| `Medication` | A medication's name, dosage and instructions, owned by a user |
| `MedicationSchedule` | When a medication is taken: reminder time, days of the week, active flag |
| `Dose` | Whether one scheduled dose was taken, missed or is still pending |

## Project structure

```
server/
├── app/                    # application package and configuration
│   ├── __init__.py
│   └── config.py
├── extensions.py           # shared extension objects (db, bcrypt, migrate)
├── models/                 # SQLAlchemy models
│   ├── user.py
│   ├── medication.py
│   ├── medication_schedule.py
│   └── dose.py
├── routes/                 # API endpoints (one blueprint per resource)
│   ├── auth_routes.py
│   ├── medication_routes.py
│   ├── schedules.py
│   ├── dose_routes.py
│   └── reports_routes.py
├── schemas/                # Marshmallow validation and serialization
├── services/               # reminder and adherence logic
├── seed.py                 # example data for all models
└── Pipfile                 # dependencies
```

## Installation

Requirements: Python 3.8 or newer, Git and [Pipenv](https://pipenv.pypa.io/).

```bash
git clone https://github.com/Enos22/flask-c10-summative-lab-sessions-and-jwt-clients.git
cd flask-c10-summative-lab-sessions-and-jwt-clients/server
pipenv install
pipenv shell
```

`pipenv install` reads the `Pipfile` and installs the dependencies, and `pipenv shell` activates the environment.

### Set up the database

<!-- TODO (lead): confirm these commands once the app factory and extensions.py are working. -->
```bash
flask db init        # only if the migrations/ folder does not exist yet
flask db migrate -m "Create tables"
flask db upgrade
python seed.py
```

`flask db migrate` generates the migration from the models, `flask db upgrade` creates the tables, and `seed.py` fills them with example users, medications, schedules and doses.

## Running the app

<!-- TODO (lead): confirm the exact command (for example whether FLASK_APP must be set). -->
```bash
flask run
```

The API is then available at `http://127.0.0.1:5000`.

## Running the tests

<!-- TODO (team): add the test folder and confirm this command. -->
```bash
pipenv run pytest
```

## API endpoints

All endpoints except signup and login require a logged-in user and return `401` otherwise.

### Authentication

<!-- TODO (Enos): list signup, login, logout and the check-session / me endpoint with methods, paths, bodies and status codes. -->

### Medications

<!-- TODO (Benson): list the medication CRUD endpoints with methods, paths, bodies and status codes. -->

### Schedules (`/api/schedules`)

| Method | Path | Description | Success | Errors |
|---|---|---|---|---|
| `GET` | `/api/schedules` | List the logged-in user's schedules, paginated | `200` | `401` |
| `GET` | `/api/schedules/<id>` | Get one schedule | `200` | `401`, `404` |
| `POST` | `/api/schedules` | Create a schedule for one of the user's medications | `201` | `401`, `404`, `422` |
| `PATCH` / `PUT` | `/api/schedules/<id>` | Update any of the schedule's fields | `200` | `401`, `404`, `422` |
| `DELETE` | `/api/schedules/<id>` | Delete a schedule | `204` | `401`, `404` |

**Pagination.** `GET /api/schedules` accepts `page` (default `1`), `per_page` (default `10`, maximum `50`) and an optional `medication_id` filter. It returns:

```json
{
  "items": [],
  "page": 1,
  "per_page": 10,
  "total": 0,
  "pages": 0
}
```

**Schedule fields**

| Field | Type | Notes |
|---|---|---|
| `id` | integer | Read only |
| `medication_id` | integer | Required on create; must belong to the logged-in user |
| `reminder_time` | string | Required, `"HH:MM"` in 24-hour time, for example `"08:30"` |
| `days_of_week` | list of strings | Required, at least one of `mon`, `tue`, `wed`, `thu`, `fri`, `sat`, `sun`; stored in week order |
| `is_active` | boolean | Optional, defaults to `true` |

**Example request**

```json
POST /api/schedules
{
  "medication_id": 1,
  "reminder_time": "08:30",
  "days_of_week": ["wed", "mon"]
}
```

**Example response** (`201`)

```json
{
  "id": 1,
  "medication_id": 1,
  "reminder_time": "08:30",
  "days_of_week": ["mon", "wed"],
  "is_active": true
}
```

A schedule that belongs to another user's medication returns `404`, not `403`, so the API does not reveal that it exists. Validation problems return `422` with a message for each invalid field.

### Doses

<!-- TODO (Wayne): list the dose endpoints (view scheduled doses, mark taken, mark missed) with methods, paths, bodies and status codes. -->

### Reports

<!-- TODO (Faith): list the report endpoints (upcoming reminders, adherence, daily report) with methods, paths and status codes. -->

## Team and responsibilities

| Member | Module | Files |
|---|---|---|
| Enos Arenga | Authentication and users: signup, login, logout, password hashing, access protection | `routes/auth_routes.py`, `models/user.py`, `schemas/user_schema.py` |
| Benson Maina | Medication management: add, view, update and delete medications | `routes/medication_routes.py`, `models/medication.py`, `schemas/medication_schema.py` |
| Samadi | Medication scheduling: create, update and delete schedules, reminder times, days of the week | `routes/schedules.py`, `models/medication_schedule.py`, `schemas/schedule_schema.py` |
| Wayne Markouma | Dose tracking: show scheduled doses, mark taken or missed, record when taken | `routes/dose_routes.py`, `models/dose.py`, `schemas/dose_schema.py` |
| Faith | Reminders and reports: upcoming reminders, adherence, daily reports | `routes/reports_routes.py`, `services/reminder_service.py`, `services/adherence_service.py` |

The team lead coordinates the shared setup (`app/__init__.py`, `extensions.py`, the dependency file), the database migrations, code reviews and the final integration.

## Team workflow

- Each member works on their own feature branch and merges through a pull request.
- Shared files (`app/__init__.py`, `extensions.py`, the dependency file) are edited only by the lead.
- Pull requests are reviewed and merged by the lead, not by their author.
- Database relationships and response formats are agreed before development, and one person coordinates the migrations.