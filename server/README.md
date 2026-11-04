# MediReminder Backend

## Description

MediReminder is a REST API backend for a medication reminder app. Users sign up, log in, and manage their own medications, the schedules for taking them, and a record of whether each dose was taken or missed. The API serves a React frontend and is built with Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-Bcrypt and Marshmallow, using SQLite for storage.

Every resource is owned by a user, and users can only see and change their own data.

Authentication is session-based: logging in stores the user's id in the session cookie, and protected routes return `401` when nobody is logged in.

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
├── app/
│   ├── __init__.py         # application factory (create_app)
│   ├── app.py              # compatibility shim for older scripts
│   └── config.py           # app and database configuration
├── extensions.py           # shared db, bcrypt, migrate and api objects
├── models/                 # SQLAlchemy models
│   ├── user.py
│   ├── medication.py
│   ├── medication_schedule.py
│   └── dose.py
├── routes/                 # API endpoints, one blueprint per resource
│   ├── auth_routes.py
│   ├── medication_routes.py
│   ├── schedules.py
│   ├── dose_routes.py
│   └── reports_routes.py
├── schemas/                # Marshmallow validation and serialization
├── services/               # reminder and adherence logic
├── migrations/             # Flask-Migrate files
├── tests/                  # automated tests
├── run.py                  # starts the app
├── seed.py                 # example data for all models
└── Pipfile                 # dependencies
```

`app/__init__.py` is the only application factory, and `run.py` starts it.

## Installation

Requirements: Python 3.8 or newer, Git, and [Pipenv](https://pipenv.pypa.io/).

```bash
git clone https://github.com/Enos22/flask-c10-summative-lab-sessions-and-jwt-clients.git
cd flask-c10-summative-lab-sessions-and-jwt-clients/server
pipenv install
pipenv shell
```

`pipenv install` reads the `Pipfile` and installs the dependencies, and `pipenv shell` activates the environment.

If you prefer plain pip, run `pip install -r requirements.txt` from the `server` directory instead.

### Database

The tables are created automatically when the app starts (`db.create_all()`). Use migrations when you change the model definitions:

```bash
flask --app run.py db init        # only if the migrations/ folder does not exist
flask --app run.py db migrate -m "describe the change"
flask --app run.py db upgrade
```

For an existing database, do not delete the database file or the `migrations` folder. Back up the database before changing the schema.

### Seed data

<!-- TODO (team): confirm this command against seed.py. -->
```bash
python seed.py
```

This creates example users, medications, schedules and doses.

## Running the app

From the `server` directory:

```bash
python run.py
```

The API runs at `http://127.0.0.1:5555` in debug mode.

### Running the frontend

```bash
cd client-with-sessions
npm install
npm start
```

The React app opens at `http://localhost:4000` and forwards API requests to port `5555`. The API accepts requests only from `http://localhost:4000`, and fetch calls from React must include `credentials: "include"` so the session cookie is sent. If the frontend moves to another address, update the CORS origin in `app/__init__.py`.

## Running the tests

<!-- TODO (team): confirm the test command. -->
```bash
pytest
```

## API endpoints

Every endpoint except signup and login requires a logged-in user and returns `401` otherwise.

### Authentication

| Method | Path | Description |
|---|---|---|
| `POST` | `/signup` | Create a user account |
| `POST` | `/login` | Log in and start a session |
| `DELETE` | `/logout` | Log out and end the session |
| `GET` | `/check_session` | Return the logged-in user, so users stay logged in on refresh |

### Medications

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/medications/addmedication` | Add a medication |
| `GET` | `/api/medications/getmedications` | List the logged-in user's medications |
| `GET` | `/api/medications/getmedication/<id>` | Get one medication |
| `PATCH` | `/api/medications/update/<id>` | Update a medication |
| `DELETE` | `/api/medications/delete/<id>` | Delete a medication |

### Schedules

| Method | Path | Description | Success | Errors |
|---|---|---|---|---|
| `GET` | `/api/schedules` | List the logged-in user's schedules, paginated | `200` | `401` |
| `GET` | `/api/schedules/<id>` | Get one schedule | `200` | `401`, `404` |
| `POST` | `/api/schedules` | Create a schedule for one of the user's medications | `201` | `401`, `404`, `422` |
| `PATCH` / `PUT` | `/api/schedules/<id>` | Update a schedule | `200` | `401`, `404`, `422` |
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

The dose resource is `/api/doses`.

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/doses` | List the logged-in user's scheduled doses |
| `GET` | `/api/doses/<id>` | Get one dose |
| `PATCH` | `/api/doses/<id>/taken` | Mark a dose as taken and record when |
| `PATCH` | `/api/doses/<id>/missed` | Mark a dose as missed |

### Reports

<!-- TODO (Faith): replace this row with the exact report paths and what each returns. -->
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/reports/...` | Daily and historical adherence reports, upcoming reminders |

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
