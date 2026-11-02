"""Reports and reminder endpoints for MediReminder.

Owner: Fiona (Reminders & Reports)

All routes require a logged-in user (session-based auth). The session is
expected to hold the user's id under session["user_id"]; confirm this key
with the Authentication module (Enos).

Endpoints (all under /api/reports):
    GET /daily                   one day's doses + summary   ?date=YYYY-MM-DD
    GET /history                 per-day summaries           ?start=&end=
    GET /adherence               overall + per-medication    ?days=30
    GET /missed                  missed doses                ?start=&end=
    GET /completed               taken doses                 ?start=&end=
    GET /reminders/upcoming      what is coming up           ?minutes=60
    GET /reminders/due           what is due / overdue now   ?overdue=60
"""
from datetime import date, datetime, timedelta
from functools import wraps

import os

from flask import Blueprint, Flask, jsonify, request, session

from server.extensions import db
from server.services import adherence_service, reminder_service

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def login_required(view):
    """Reject the request unless a user is logged in.

    If the Authentication module provides a shared decorator, import that
    instead and delete this one so everyone uses the same behaviour.
    """

    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return view(*args, **kwargs)

    return wrapped


def parse_date(value, default):
    """Parse YYYY-MM-DD. Returns (date, error_message)."""
    if not value:
        return default, None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date(), None
    except ValueError:
        return None, f"Invalid date '{value}'. Use YYYY-MM-DD."


def parse_int(name, default, minimum=0, maximum=10000):
    """Read a positive integer query parameter. Returns (int, error_message)."""
    raw = request.args.get(name)
    if raw is None:
        return default, None
    try:
        number = int(raw)
    except ValueError:
        return None, f"'{name}' must be a whole number."
    if not (minimum <= number <= maximum):
        return None, f"'{name}' must be between {minimum} and {maximum}."
    return number, None


def date_range(default_days=7):
    """Read ?start= and ?end= (inclusive). Returns (start, end, error)."""
    today = date.today()
    end, err = parse_date(request.args.get("end"), today)
    if err:
        return None, None, err
    start, err = parse_date(request.args.get("start"), end - timedelta(days=default_days - 1))
    if err:
        return None, None, err
    if start > end:
        return None, None, "'start' must not be after 'end'."
    if (end - start).days > 366:
        return None, None, "Date range cannot exceed one year."
    return start, end, None


def error(message, status=400):
    return jsonify({"error": message}), status


# --------------------------------------------------------------------------
# Reports
# --------------------------------------------------------------------------
@reports_bp.get("/daily")
@login_required
def daily_report():
    """Everything for one day: doses grouped by status, plus a summary."""
    day, err = parse_date(request.args.get("date"), date.today())
    if err:
        return error(err)

    user_id = session["user_id"]
    if day == date.today():
        # Make sure today's pending doses exist so the report is complete.
        reminder_service.generate_doses_for_date(user_id, day)

    doses = adherence_service.fetch_dose_dicts(user_id, day, day)
    return jsonify({
        "date": day.isoformat(),
        "summary": adherence_service.summarize(d["status"] for d in doses),
        "taken": [d for d in doses if d["status"] == "taken"],
        "missed": [d for d in doses if d["status"] == "missed"],
        "pending": [d for d in doses if d["status"] == "pending"],
    })


@reports_bp.get("/history")
@login_required
def history_report():
    """A summary for each day in a range (default: last 7 days)."""
    start, end, err = date_range(default_days=7)
    if err:
        return error(err)

    return jsonify({
        "start": start.isoformat(),
        "end": end.isoformat(),
        "days": adherence_service.daily_history(session["user_id"], start, end),
    })


@reports_bp.get("/adherence")
@login_required
def adherence_report():
    """Overall adherence over the last N days, with a per-medication split."""
    days, err = parse_int("days", 30, minimum=1, maximum=366)
    if err:
        return error(err)

    end = date.today()
    start = end - timedelta(days=days - 1)
    return jsonify(adherence_service.calculate_adherence(session["user_id"], start, end))


@reports_bp.get("/missed")
@login_required
def missed_doses():
    """Missed doses in a range (default: last 7 days), newest first."""
    start, end, err = date_range(default_days=7)
    if err:
        return error(err)

    doses = adherence_service.fetch_dose_dicts(session["user_id"], start, end)
    missed = [d for d in doses if d["status"] == "missed"]
    missed.sort(key=lambda d: d["scheduled_time"], reverse=True)
    return jsonify({"start": start.isoformat(), "end": end.isoformat(),
                    "count": len(missed), "doses": missed})


@reports_bp.get("/completed")
@login_required
def completed_doses():
    """Taken doses in a range (default: last 7 days), newest first."""
    start, end, err = date_range(default_days=7)
    if err:
        return error(err)

    doses = adherence_service.fetch_dose_dicts(session["user_id"], start, end)
    taken = [d for d in doses if d["status"] == "taken"]
    taken.sort(key=lambda d: d["scheduled_time"], reverse=True)
    return jsonify({"start": start.isoformat(), "end": end.isoformat(),
                    "count": len(taken), "doses": taken})


# --------------------------------------------------------------------------
# Reminders
# --------------------------------------------------------------------------
@reports_bp.get("/reminders/upcoming")
@login_required
def upcoming_reminders():
    """Doses coming up in the next N minutes (default 60)."""
    minutes, err = parse_int("minutes", 60, minimum=1, maximum=1440)
    if err:
        return error(err)

    reminders = reminder_service.get_upcoming_reminders(session["user_id"], minutes)
    return jsonify({"window_minutes": minutes, "count": len(reminders),
                    "reminders": reminders})


@reports_bp.get("/reminders/due")
@login_required
def due_reminders():
    """Doses due now or overdue (but not yet marked) within the last N minutes."""
    overdue, err = parse_int("overdue", 60, minimum=1, maximum=1440)
    if err:
        return error(err)

    reminders = reminder_service.get_due_reminders(session["user_id"], overdue)
    return jsonify({"overdue_minutes": overdue, "count": len(reminders),
                    "reminders": reminders})


# --------------------------------------------------------------------------
# App setup 
# --------------------------------------------------------------------------
def create_app():
    """Create a Flask app with only the reports routes, for running/testing."""
    app = Flask(__name__)

    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(base_dir, "medireminder.db")
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.register_blueprint(reports_bp)

    # Testing shortcuts until the real login from the auth module is merged.
    if app.debug or os.environ.get("ENABLE_DEV_LOGIN") == "1":

        @app.get("/dev/login/<int:user_id>")
        def dev_login(user_id):
            session["user_id"] = user_id
            return jsonify({"message": f"Logged in as user {user_id} (dev only)"})

        @app.get("/dev/logout")
        def dev_logout():
            session.clear()
            return jsonify({"message": "Logged out"})

    with app.app_context():
        from server import models  # noqa: F401  (registers the tables)
        db.create_all()

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)