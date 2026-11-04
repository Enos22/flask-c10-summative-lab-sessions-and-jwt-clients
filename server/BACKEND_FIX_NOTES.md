# Backend consistency fixes

## Canonical app entry point
`app/__init__.py` is now the only application factory. `run.py` starts it.
`app/app.py` remains as a compatibility shim for older scripts.

## Shared extensions
`extensions.py` is the canonical location for `db`, `bcrypt`, `migrate`, and
`api`. `extension.py` only re-exports those same objects.

## API endpoints
- Auth: `POST /signup`, `POST /login`, `DELETE /logout`, `GET /check_session`
- Medication: `POST /api/medications/addmedication`
- Medication: `GET /api/medications/getmedications`
- Medication: `GET /api/medications/getmedication/<id>`
- Medication: `PATCH /api/medications/update/<id>`
- Medication: `DELETE /api/medications/delete/<id>`
- Doses: `GET /api/doses`, `GET /api/doses/<id>`
- Doses: `PATCH /api/doses/<id>/taken`, `PATCH /api/doses/<id>/missed`
- Schedules: `GET/POST /api/schedules`
- Schedules: `GET/PATCH/PUT/DELETE /api/schedules/<id>`
- Reports: `/api/reports/...`

The dose resource is `/api/doses`, not `/api/dosages`.
The schedule resource is `/api/schedules`; it is separate from medication CRUD.

## CORS and sessions
CORS permits exactly `http://localhost:4000` and credentials. React fetch calls
must include `credentials: "include"`. If the frontend is moved to another
origin, update the CORS origin in `app/__init__.py`.

## Install and run
From the `server` directory:
```bash
pip install -r requirements.txt
python run.py
```

For migrations, use:
```bash
flask --app run.py db init
flask --app run.py db migrate -m "initial schema"
flask --app run.py db upgrade
```
The project currently calls `db.create_all()` during app startup for continuity
with the uploaded version. For an existing database, do not delete the database
or migrations folder. Back up the database before changing schema definitions.
