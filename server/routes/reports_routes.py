"""Reports and reminder endpoints for MediReminder.

Owner: Fiona (Reminders & Reports)

Follows the team's pattern (see auth_routes.py): import the shared `app`
from app.config, register routes on it, and run this file directly.

Run from the server/ folder:
    python -m routes.reports_routes

Login is handled by auth_routes.py (session["user_id"]). Its global
before_request already returns 401 to anyone not logged in.

Endpoints (all under /api/reports):
    GET /daily                   one day's doses + summary   ?date=YYYY-MM-DD
    GET /history                 per-day summaries           ?start=&end=
    GET /adherence               overall + per-medication    ?days=30
    GET /missed                  missed doses                ?start=&end=
    GET /completed               taken doses                 ?start=&end=
    GET /reminders/upcoming      what is coming up           ?minutes=60
    GET /reminders/due           what is due / overdue now   ?overdue=60

All dates are local dates (Nairobi by default); times are returned in UTC
with a trailing Z so the React app can show them in local time.
"""
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request, session

from app.config import app
from services import adherence_service, reminder_service

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@reports_bp.before_request
def require_login():
    if not session.get("user_id"):
        return jsonify({"error": "Authentication required."}), 401


def _user_id():
    return session.get("user_id")


def error(message, status=400):
    return jsonify({"error": message}), status


def parse_date(value, default):
    """Parse YYYY-MM-DD. Returns (date, error_message)."""
    if not value:
        return default, None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date(), None
    except ValueError:
        return None, f"Invalid date '{value}'. Use YYYY-MM-DD."


def parse_int(name, default, minimum=0, maximum=10000):
    """Read an integer query parameter. Returns (int, error_message)."""
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
    today = reminder_service.local_today()
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


# --------------------------------------------------------------------------
# Reports
# --------------------------------------------------------------------------
@reports_bp.get("/daily")
def daily_report():
    """Everything for one day: doses grouped by status, plus a summary."""
    today = reminder_service.local_today()
    day, err = parse_date(request.args.get("date"), today)
    if err:
        return error(err)

    if day == today:
        # Make sure today's pending doses exist so the report is complete.
        reminder_service.generate_doses_for_date(_user_id(), day)

    doses = adherence_service.fetch_dose_dicts(_user_id(), day, day)
    return jsonify({
        "date": day.isoformat(),
        "summary": adherence_service.summarize(d["status"] for d in doses),
        "taken": [d for d in doses if d["status"] == "taken"],
        "missed": [d for d in doses if d["status"] == "missed"],
        "pending": [d for d in doses if d["status"] == "pending"],
    })


@reports_bp.get("/history")
def history_report():
    """A summary for each day in a range (default: last 7 days)."""
    start, end, err = date_range(default_days=7)
    if err:
        return error(err)
    return jsonify({
        "start": start.isoformat(),
        "end": end.isoformat(),
        "days": adherence_service.daily_history(_user_id(), start, end),
    })


@reports_bp.get("/adherence")
def adherence_report():
    """Overall adherence over the last N days, with a per-medication split."""
    days, err = parse_int("days", 30, minimum=1, maximum=366)
    if err:
        return error(err)
    end = reminder_service.local_today()
    start = end - timedelta(days=days - 1)
    return jsonify(adherence_service.calculate_adherence(_user_id(), start, end))


def _doses_with_status(status):
    start, end, err = date_range(default_days=7)
    if err:
        return error(err)
    doses = adherence_service.fetch_dose_dicts(_user_id(), start, end)
    matching = [d for d in doses if d["status"] == status]
    matching.sort(key=lambda d: d["scheduled_time"], reverse=True)
    return jsonify({"start": start.isoformat(), "end": end.isoformat(),
                    "count": len(matching), "doses": matching})


@reports_bp.get("/missed")
def missed_doses():
    """Missed doses in a range (default: last 7 days), newest first."""
    return _doses_with_status("missed")


@reports_bp.get("/completed")
def completed_doses():
    """Taken doses in a range (default: last 7 days), newest first."""
    return _doses_with_status("taken")


# --------------------------------------------------------------------------
# Reminders
# --------------------------------------------------------------------------
@reports_bp.get("/reminders/upcoming")
def upcoming_reminders():
    """Doses coming up in the next N minutes (default 60)."""
    minutes, err = parse_int("minutes", 60, minimum=1, maximum=1440)
    if err:
        return error(err)
    reminders = reminder_service.get_upcoming_reminders(_user_id(), minutes)
    return jsonify({"window_minutes": minutes, "count": len(reminders),
                    "reminders": reminders})


@reports_bp.get("/reminders/due")
def due_reminders():
    """Doses due now or overdue (not yet marked) within the last N minutes."""
    overdue, err = parse_int("overdue", 60, minimum=1, maximum=1440)
    if err:
        return error(err)
    reminders = reminder_service.get_due_reminders(_user_id(), overdue)
    return jsonify({"overdue_minutes": overdue, "count": len(reminders),
                    "reminders": reminders})


app.register_blueprint(reports_bp)


if __name__ == "__main__":
    app.run(port=5555, debug=True)